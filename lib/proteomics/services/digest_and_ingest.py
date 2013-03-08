from proteomics.models import (File, FileDigest, Taxon, Protein, 
                               ProteinInstance, ProteinDigest, Peptide, 
                               PeptideInstance, TaxonDigest, Digest, Protease)
from proteomics import db
from proteomics.util.digest import cleave
from proteomics.util.logging_util import LoggerLogHandler
from pyteomics import fasta
import os
import hashlib
import logging
from sqlalchemy.orm import sessionmaker


class DigestAndIngestTask(object):
    def __init__(self, logger=logging.getLogger(), fasta_paths=[], 
                 digest_def=None, get_connection=None, **kwargs):
        self.logger = logger
        self.fasta_paths = fasta_paths
        self.digest_def = digest_def

        # Assign get_connection function.
        if not get_connection:
            def get_connection():
                engine = create_engine('sqlite://')
                return engine.connect()
        self.get_connection = get_connection

    def run(self):
        # Initialize stats dict.
        self.stats = {
            'Taxon': 0,
            'Protein': 0,
            'ProteinInstance': 0,
            'Peptide': 0,
            'PeptideInstance': 0,
        }

        # get db session.
        self.connection = self.get_connection()
        self.session = sessionmaker()(bind=self.connection)

        # Get protease.
        protease = self.session.query(Protease).get(
            self.digest_def.get('protease_id'))

        # Get or create digest object.
        self.digest = (
            self.session.query(Digest)
            .filter(Digest.protease == protease)
            .filter(Digest.max_missed_cleavages == self.digest_def.get(
                'max_missed_cleavages'))
        ).first()
        if not self.digest:
            self.digest = Digest(
                protease=protease,
                max_missed_cleavages=self.digest_def.get(
                    'max_missed_cleavages')
            )
            self.session.add(self.digest)
            self.session.commit()

        # Process FASTA files.
        for path in self.fasta_paths:
            self.process_fasta_file(path)

        self.logger.info("Digest and Ingest complete.")
        self.logger.info("Ingest stats: %s" % self.stats)
        return self.stats

    def process_fasta_file(self, path):
        base_msg = "Processing file '%s'..." % path
        file_logger = self.get_child_logger(id(path), base_msg,
                                            self.logger)

        # Get or create File object.
        checksum = self.get_checksum(path)
        file_ = File(id=checksum, basename=os.path.basename(path))
        file_ = self.session.merge(file_)

        # If digest has been run on this file, don't do anything.
        if self.session.query(FileDigest).get((file_.id, self.digest.id)):
            file_logger.info((
                "File '%s' has already been digested with"
                " digest '%s', skipping."
            ) % (path, self.digest))
            return
        # Otherwise create a new file digest.
        else:
            file_digest = FileDigest(file_, self.digest)
            self.session.add(file_digest)
            self.session.commit()

        # Get taxon from filename.
        taxon_id = os.path.splitext(os.path.basename(path))[0]

        # Get taxon object from db or create a new one.
        taxon = self.session.query(Taxon).get(taxon_id)
        if not taxon:
            taxon = Taxon(id=taxon_id)
            self.session.add(taxon)
            self.session.commit()
            self.stats['Taxon'] += 1
            file_logger.info("Created taxon '%s'" % taxon_id)

        # Get taxon digest object from db or create a new one.
        taxon_digest = (
            self.session.query(TaxonDigest)
            .filter(TaxonDigest.taxon == taxon)
            .filter(TaxonDigest.digest == self.digest)
        ).first()
        if not taxon_digest:
            taxon_digest = TaxonDigest(taxon=taxon, digest=self.digest)
            self.session.add(taxon_digest)
            self.session.commit()

        # Process protein sequences in batches.
        file_logger.info("Counting # of protein sequences...")
        num_proteins = 0
        for metadata, sequence in fasta.read(path):
            num_proteins += 1
        file_logger.info("%s total protein sequences." % num_proteins)
        batch_size = 1e4
        batch_counter = 0
        batch = []
        protein_logger = self.get_child_logger(
            "%s_proteins" % id(file_logger), "Processing proteins...",
            file_logger
        )
        protein_logger.info("")
        for metadata, sequence in fasta.read(path):
            batch.append((metadata, sequence,))
            batch_counter += 1
            if (batch_counter % batch_size) == 0:
                self.process_protein_batch(
                    batch, taxon, logger=protein_logger)
                protein_logger.info(
                    ("%s of %s (%.1f%%)") % (
                        batch_counter, num_proteins, 
                        100.0 * batch_counter/num_proteins
                    )
                )
                batch = []
        self.process_protein_batch(
            batch, taxon, logger=protein_logger)
        self.logger.info("Done processing file '%s'" % path)

    def get_checksum(self, path):
        sha1 = hashlib.sha1()
        with open(path, 'rb') as f:
            while True:
                data = f.read(8192)
                if not data: break
                sha1.update(data)
        return sha1.hexdigest()

    def process_protein_batch(self, batch, taxon, logger=None):
        """ Process a batch of proteins with the given digest. """
        if not logger:
            logger = self.logger
        # Get existing proteins by searching for sequences.
        existing_proteins = {}
        for protein in (
            self.session.query(Protein)
            .filter(Protein.sequence.in_(
                [sequence for metadata, sequence in batch])
            )
        ):
            existing_proteins[protein['sequence']] = protein

        # Initialize collection of undigested proteins.
        undigested_proteins = {}
        digested_proteins = {}
        if existing_proteins:
            for protein_digest in (
                self.session.query(Protein)
                .filter(Protein.id.in_(
                    [protein.id for protein in existing_proteins.values()]))
                .join(ProteinDigest)
                .filter(ProteinDigest.digest == self.digest)
            ):
                protein = protein_digest.protein
                digested_proteins[protein.sequence] = protein
        for protein in existing_proteins.values():
            if protein.sequence not in digested_proteins:
                undigested_proteins[protein.sequence] = protein
        
        # Create proteins which do not exist in the db and add to undigested
        # collection.
        num_new_proteins = 0
        for metadata, sequence in batch:
            if sequence not in existing_proteins:
                num_new_proteins += 1
                protein = Protein(sequence=sequence)
                self.session.add(protein)
                existing_proteins[sequence] = protein
                undigested_proteins[sequence] = protein
        logger.info("creating %s new proteins..." % (
            num_new_proteins))
        self.session.commit()
        self.stats['Protein'] += num_new_proteins

        # Digest undigested proteins.
        if undigested_proteins:
            num_undigested = len(undigested_proteins)
            logger.info("digesting %s proteins" % num_new_proteins)
            undigested_batch = {}
            peptide_counter = 0
            for protein in undigested_proteins.values():
                peptide_sequences = cleave(
                    protein.sequence, self.digest.protease.cleavage_rule, 
                    self.digest.max_missed_cleavages
                )
                peptide_counter += len(peptide_sequences)
                undigested_batch[protein] = peptide_sequences
                if (peptide_counter > 1e4):
                    self.process_peptide_batch(undigested_batch, logger)
                    peptide_counter = 0
            self.process_peptide_batch(undigested_batch, logger)

        # Create protein instances in bulk.
        protein_instance_dicts = []
        for metadata, sequence in batch:
            protein = existing_proteins[sequence]
            protein_instance_dicts.append({
                'protein_id': protein.id,
                'taxon_id': taxon.id
            })
        logger.info("Creating %s new protein instances..." % (
            len(protein_instance_dicts)))
        self.session.execute(
            db.tables['ProteinInstance'].insert(), protein_instance_dicts)
        self.stats['ProteinInstance'] += len(protein_instance_dicts)

    def process_peptide_batch(self, batch, logger=None):
        if not logger:
            logger = self.logger
        combined_peptide_sequences = set()
        for protein, peptide_sequences in batch.items():
            for sequence in peptide_sequences:
                combined_peptide_sequences.add(sequence)

        # Get existing peptides.
        existing_peptides = {}
        existing_peptides_batch = []
        existing_peptides_counter = 0
        for sequence in combined_peptide_sequences:
            existing_peptides_counter += 1
            existing_peptides_batch.append(sequence)
            if (existing_peptides_counter % 500) == 0:
                self.update_existing_peptides_(
                    existing_peptides_batch, existing_peptides)
                existing_peptides_batch = []
        self.update_existing_peptides_(
            existing_peptides_batch, existing_peptides)

        # Create non-existent peptides in bulk.
        num_new_peptides = 0
        peptide_dicts = []
        for sequence in combined_peptide_sequences:
            if sequence not in existing_peptides:
                num_new_peptides += 1
                peptide_dicts.append({
                    'sequence': sequence
                })
        logger.info("Creating %s new peptides..." % num_new_peptides)
        self.session.execute(db.tables['Peptide'].insert(), peptide_dicts)
        self.stats['Peptide'] += num_new_peptides

        # Get newly created peptide objects and add to existing peptides.
        created_peptides_batch = []
        created_peptides_counter = 0
        for peptide_dict in peptide_dicts:
            created_peptides_counter += 1
            created_peptides_batch.append(peptide_dict['sequence'])
            if (created_peptides_counter % 500) == 0:
                self.update_existing_peptides_(created_peptides_batch, 
                                               existing_peptides)
                created_peptides_batch = []
        self.update_existing_peptides_(
            created_peptides_batch, existing_peptides)

        # Create peptide instances in bulk.
        num_peptide_instances = 0
        for protein, peptide_sequences in batch.items():
            for sequence in peptide_sequences:
                num_peptide_instances += 1
        logger.info("Creating %s new peptide instances..." % (
            num_peptide_instances))
        peptide_instance_batch = []
        peptide_instance_counter = 0
        for protein, peptide_sequences in batch.items():
            for sequence in peptide_sequences:
                peptide_instance_counter += 1
                peptide = existing_peptides[sequence]
                peptide_instance_batch.append({
                    'peptide_id': peptide.id,
                    'protein_id': protein.id,
                    'digest_id': self.digest.id,
                })
                if (peptide_instance_counter % 1e4) == 0:
                    session.execute(
                        db.tables['PeptideInstance'].insert(),
                        peptide_instance_batch)
        self.session.execute(
            db.tables['PeptideInstance'].insert(), peptide_instance_batch)
        self.stats['PeptideInstance'] += num_peptide_instances

    def update_existing_peptides_(self, sequences, existing_peptides):
        for peptide in (
            self.session.query(Peptide).filter(Peptide.sequence.in_(sequences))
        ):
            existing_peptides[peptide.sequence] = peptide

    def get_child_logger(self, name=None, base_msg=None, parent_logger=None):
        if not parent_logger:
            parent_logger = self.logger
        logger = logging.getLogger("%s_%s" % (id(self), name))
        formatter = logging.Formatter(base_msg + ' %(message)s.')
        log_handler = LoggerLogHandler(parent_logger)
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)
        logger.setLevel(parent_logger.level)
        return logger

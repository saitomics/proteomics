"""
Utility to ingest a FASTA file into the db.
"""

from proteomics import db
from proteomics.models import Protein, Digest, DigestProduct
from pyteomics import fasta, parser

class FastaIngestor(object):

    def __init__(self):
        self.session = db.get_session()

    def ingest(self, fasta_file, digest_id='trypsin'):
        detached_digest = Digest(digest_id)
        digest = self.session.merge(detached_digest)

        protein_records = read_fasta_records(fasta_file)
        for protein_record in protein_records:
            detached_protein = Protein(sequence=protein_record['sequence'])
            protein = self.session.merge(detached_protein)

            # Save peptide records if protein has not been digested.
            if not self.protein_has_been_digested(protein, digest):
                peptide_sequences = self.digest_protein(
                    protein.sequence, 
                    digest.id
                )
                for peptide_sequence in peptide_sequences:
                    detached_peptide = Peptide(peptide_sequence)
                    peptide = self.session.merge(detached_peptide)
                    # @TODO: schema flaw here.
                    # if a protein digest produces the same
                    # peptide multiple times, we need to record
                    # how many times that peptide is produced.
                    # current schema will clobber duplicates, which
                    # may not be what we want.
                    digest_product = self.session.merge(DigestProduct(protein, digest, peptide)



    def read_fasta_records(self, fasta_file):
        """ Read sequence records from a FASTA file. """
        records = []
        for description, sequence in fasta.read(fasta_file):
            records.append({
                'sequence': sequence,
                'metadata': metadata
            })
        return records

    def digest_protein(self, sequence, digest_id):
        peptide_sequences = parser.cleave(
            sequence, 
            parser.expasy_rules[digest_id],
            missed_cleavages=1 #max no. of missed cleavages.
        )
        return peptide_sequences

    def protein_has_been_digested(self, protein, digest):
        return self.session.query(DigestProduct)\
                .filter(DigestProduct.protein == protein)\
                .filter(DigestProduct.digest == digest)\
                .count() > 0

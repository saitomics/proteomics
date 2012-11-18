"""
Ingestion services.
"""

from proteomics import db
from proteomics import models
from pyteomics import fasta, parser

class FastaIngestService(object):
    """ Ingest protein records from a FASTA File. """

    def ingest(self, fasta_file=None, proteome=None, session=db.session()):
        # HANDLE GENOME HERE.
        # THROW ERROR IF DUPE?

        # Read protein records from fasta.
        protein_records = [{'metadata': metadata, 'sequence': sequence} 
                           for metadata, sequence in fasta.read(fasta_file)]

        # Count unique proteins.
        unique_proteins = set()

        # Count new records.
        new_proteins = 0
        new_instances = 0

        for protein_record in protein_records:
            protein = models.Protein(sequence=protein_record['sequence'])
            # Merge to avoid duplicate records for the same protein sequence.
            protein = session.merge(protein)
            if db.get_obj_state(protein) == 'pending':
                new_proteins += 1
            unique_proteins.add(protein)
            
            # Create protein instance.
            protein_instance = models.ProteinInstance(
                protein=protein,
                proteome=proteome,
                metadata=protein_record['metadata']
            )
            session.add(protein_instance)
            new_instances += 1

        # Save records.
        session.commit()

        # Return stats.
        return {
            'unique_proteins': len(unique_proteins),
            'new_proteins': new_proteins,
            'new_protein_instances': new_instances
        }

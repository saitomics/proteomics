"""
Utility to ingest a FASTA file into the db.
"""

from pyteomics import fasta, parser

class FastaIngestor(object):
    def __init__(self): pass

    def ingest(self):
        protein_records = read_fasta_records(fasta_file)
        for protein_record in protein_records:
            # Get record obj via merge.
            # If there are no proteolysis_products for the given digest and sequence...
                # Digest the sequence.
                # Save peptide records.

    def read_fasta_records(self, fasta_file):
        """ Read sequence records from a FASTA file. """
        records = []
        for description, sequence in fasta.read(fasta_file):
            records.append({
                'sequence': sequence,
                'metadata': metadata
            })
        return records

    def digest_protein(self, sequence, digest='trypsin'):
        peptides = parser.cleave(
            sequence, 
            parser.expasy_rules[digest],
            missed_cleavages=1 #max no. of missed cleavages.
        )
        return peptides

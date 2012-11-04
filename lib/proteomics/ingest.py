"""
Utility to ingest a FASTA file into the db.
"""

from proteomics import db

def includePyteomics():
    """ 
    Some chicanery to include pyteomics. 
    Some parts of pyteomics require dependencies like 'matplotlib' or 'lxml', 
    which can be a PITA to install and distribute.
    We're not using those dependencies in this script, so we fake out
    pyteomics by pretending we have them.
    """
    class fakemodule(object):
        """ Mock stub for module imports. """
        @staticmethod
        def method(a, b):
            return a+b
    sys.modules["numpy"] = fakemodule
    sys.modules["lxml"] = fakemodule
    sys.modules["lxml"].etree = None
includePyteomics()
from pyteomics import fasta, parser

class FastaIngestor(object):
    def __init__(self, db):
        self.db = db

    def ingest(self, fasta_file):
        protein_records = read_fasta_records(fasta_file)
        for protein_record in protein_records:
            pass
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

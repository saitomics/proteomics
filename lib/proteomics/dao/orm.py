"""
Mapping from schema to objects.
"""
from .schema import metadata, tables
from sqlalchemy.orm import mapper, relationship


class Protein(object):
    def __init__(self, sequence=None):
        self.sequence = sequence

class Peptide(object):
    def __init__(self, sequence=None):
        self.sequence = sequence

class Genome(object):
    def __init__(self, id=None):
        self.id = id

class Digest(object):
    def __init__(self, id=None):
        self.id = id

class ProteinInstance(object):
    def __init__(self, protein=None, genome=None, metadata=None):
        self.protein = protein
        self.genome = genome
        self.metadata = metadata

class DigestProduct(object):
    def __init__(self, protein, digest, peptide):
        self.protein = protein
        self.digest = digset
        self.peptide = peptide

mapper(Protein, tables['proteins'])

mapper(Peptide, tables['peptides'])

mapper(Genome, tables['genomes'])

mapper(Digest, tables['digests'])

mapper(ProteinInstance, tables['protein_instances'], properties={
    'protein': relationship(Protein),
    'genome': relationship(Genome)
})

mapper(DigestProduct, tables['digest_products'], properties={
    'protein': relationship(Protein),
    'digest': relationship(Genome),
    'peptide': relationship(Peptide)
})

"""
Domain models.
"""


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
    """
    A protein instance is a single occurence of a protein
    that occurs within a dataset. Typically this dataset
    is a genome.
    We use protein records because the same protein can appear multiple
    times w/in a genome.
    """
    def __init__(self, protein=None, genome=None, metadata=None):
        self.protein = protein
        self.genome = genome
        self.metadata = metadata

class DigestProduct(object):
    """
    We represent the products of a digest as 
    protein-digest-peptide triples.
    """
    def __init__(self, protein, digest, peptide):
        self.protein = protein
        self.digest = digset
        self.peptide = peptide

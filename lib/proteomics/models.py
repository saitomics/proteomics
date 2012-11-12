"""
Domain models.
"""


class Protein(object):
    def __init__(self, id=None, sequence=None):
        self.sequence = sequence
        self.id = id or self.sequence

class Peptide(object):
    def __init__(self, id=None, sequence=None):
        self.sequence = sequence
        self.id = id or self.sequence

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
    def __init__(self, id=None, protein=None, genome=None, metadata=None):
        self.id = id
        self.protein = protein
        self.genome = genome
        self.metadata = metadata

class PeptideInstance(object):
    """
    A protein instance is a single occurence of a protein
    that occurs within a set peptides. Typically this set
    is the result of a protein digestion.
    """
    def __init__(self, id=None, protein=None, digest=None, peptide=None):
        self.id = id
        self.protein = protein
        self.digest = digset
        self.peptide = peptide

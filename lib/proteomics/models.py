"""
Domain models.
"""

class File(object):
    def __init__(self, id=None, basename=None):
        self.id = id
        self.basename = basename

class FileDigest(object):
    def __init__(self, file_=None, digest=None):
        self.file = file_
        self.digest = digest

class Taxon(object):
    def __init__(self, id=None, metadata=None):
        self.id = id
        self.metadata = metadata

class TaxonDigest(object):
    def __init__(self, id=None, taxon=None, digest=None):
        self.id = id
        self.taxon = taxon
        self.digest = digest

class Protein(object):
    def __init__(self, id=None, sequence=None, mass=None, metadata=None):
        self.id = id
        self.sequence = sequence
        self.mass = mass
        self.metadata = metadata

class ProteinDigest(object):
    def __init__(self, id=None, protein=None, digest=None):
        self.id = id
        self.protein = protein
        self.digest = digest

class ProteinInstance(object):
    """
    A protein instance is a single occurence of a protein
    that occurs within a taxon's proteome.
    We use protein records because the same protein can appear multiple
    times w/in a proteome.
    """
    def __init__(self, id=None, protein=None, taxon=None, 
                 metadata=None):
        self.id = id
        self.protein = protein
        self.taxon = taxon
        self.metadata = metadata

class Peptide(object):
    def __init__(self, id=None, sequence=None, mass=None, metadata=None):
        self.id = id
        self.sequence = sequence
        self.mass = mass
        self.metadata = metadata

class PeptideInstance(object):
    """
    A peptide instance is a peptide
    produced by a digest of a protein.
    """
    def __init__(self, id=None, peptide=None, protein=None, digest=None): 
        self.id = id
        self.peptide = peptide
        self.protein = protein
        self.digest = digest

class Protease(object):
    def __init__(self, id=None, cleavage_rule=None):
        self.id = id
        self.cleavage_rule = cleavage_rule

class Digest(object):
    def __init__(self, id=None, protease=None, max_missed_cleavages=0):
        self.id = id
        self.protease = protease 
        self.max_missed_cleavages = max_missed_cleavages

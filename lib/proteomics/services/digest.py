#@TODO: need to think on whether should separate out digest funcs from digest
# services. E.g. should digester know about db? I'm thinking not, for better
# decoupling.
# Instead the digest funcs go in a util section, and in this section
# we know about the db and the digest funcs.
# Then we do checking for whether something has already been digested.
# Yah. So figure out where to put digest funcs. Util probably.
# Digest func is just a simple digest_protein func.
# Might even just use func from pyteomics.
# In which case, funcs in this file would be better called something like
# 'get_proteome_digest_results'.
class ProteinDigester(object):
    """ Digests proteins. """

    def digest_proteome(self, proteome=None, **kwargs):
        """ Digest the given proteome. """
        unique_proteins = set(getattr(proteome, 'proteins', []))
        peptides = []
        for protein in unique_proteins:
            peptides.extend(self.digest_protein(protein, **kwargs))
        return peptides

    def digest_protein(self, protein=None, digest=None, digest_args={}, **kwargs):
        """ Digest the given protein. """
        pass

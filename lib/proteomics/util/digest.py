from collections import deque
from itertools import chain
import re


def cleave(sequence, rule, missed_cleavages=0):
    """Cleaves a polypeptide sequence using a given rule.
    Taken from pyteomics.parser .
    
    Parameters
    ----------
    sequence : str
        The sequence of a polypeptide.
    rule : str    
        A string with a regular expression describing the C-terminal site of
        cleavage.    
    missed_cleavages : int, optional
        The maximal number of allowed missed cleavages. Defaults to 0.

    Returns
    -------
    out : list
        A list of peptides.

    Examples
    --------
    >>> cleave('AKAKBK', expasy_rules['trypsin'], 0)
    ['AK', 'AK', 'BK']
    >>> cleave('AKAKBKCK', expasy_rules['trypsin'], 2)
    ['AK', 'AKAK', 'AK', 'AKAKBK', 'AKBK', 'BK', 'AKBKCK', 'BKCK', 'CK']
    """
    peptides = []
    cleavage_sites = deque([0], maxlen=missed_cleavages+2)
    for i in chain(map(lambda x: x.end(), re.finditer(rule, sequence)),
                   [None]):
        cleavage_sites.append(i)
        for j in range(0, len(cleavage_sites)-1):
            peptide = sequence[cleavage_sites[j]:cleavage_sites[-1]]
            if peptide != '':
                peptides.append(peptide)
    return peptides

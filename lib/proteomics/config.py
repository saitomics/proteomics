import os

# These cleavage rules are taken from:
# http://web.expasy.org/peptide_cutter/peptidecutter_enzymes.html,
# Included in this repo as docs/expasy_peptidecuttr_enzymes.html
CLEAVAGE_RULES = {
    'arg-c':         'R',
    'asp-n':         '\w(?=D)',
    'bnps-skatole' : 'W',
    'caspase 1':     '(?<=[FWYL]\w[HAT])D(?=[^PEDQKR])',
    'caspase 2':     '(?<=DVA)D(?=[^PEDQKR])',
    'caspase 3':     '(?<=DMQ)D(?=[^PEDQKR])',
    'caspase 4':     '(?<=LEV)D(?=[^PEDQKR])',
    'caspase 5':     '(?<=[LW]EH)D',
    'caspase 6':     '(?<=VE[HI])D(?=[^PEDQKR])',
    'caspase 7':     '(?<=DEV)D(?=[^PEDQKR])',
    'caspase 8':     '(?<=[IL]ET)D(?=[^PEDQKR])',
    'caspase 9':     '(?<=LEH)D',
    'caspase 10':    '(?<=IEA)D',
    'chymotrypsin low specificity' : '([FY](?=[^P]))|(W(?=[^MP]))',
    'chymotrypsin high specificity':
    '([FLY](?=[^P]))|(W(?=[^MP]))|(M(?=[^PY]))|(H(?=[^DMPW]))',
    'clostripain':   'R',
    'cnbr':          'M',
    'enterokinase':  '(?<=[DN][DN][DN])K',
    'factor xa':     '(?<=[AFGILTVM][DE]G)R',
    'formic acid':   'D',
    'glutamyl endopeptidase': 'E',
    'granzyme b':    '(?<=IEP)D',
    'hydroxylamine': 'N(?=G)',
    'iodosobezoic acid': 'W',
    'lysc':          'K',
    'ntcb':          '\w(?=C)',
    'pepsin ph1.3':  '((?<=[^HKR][^P])[^R](?=[FLWY][^P]))|'
    '((?<=[^HKR][^P])[FLWY](?=\w[^P]))',
    'pepsin ph2.0':  '((?<=[^HKR][^P])[^R](?=[FL][^P]))|'
    '((?<=[^HKR][^P])[FL](?=\w[^P]))',
    'proline endopeptidase': '(?<=[HKR])P(?=[^P])',
    'proteinase k':  '[AEFILTVWY]',
    'staphylococcal peptidase i': '(?<=[^E])E',
    'thermolysin':   '[^DE](?=[AFILMV])',
    'thrombin':      '((?<=G)R(?=G))|'
    '((?<=[AFGILTVM][AFGILTVWA]P)R(?=[^DE][^DE]))',
    'trypsin':       '([KR](?=[^P]))|((?<=W)K(?=P))|((?<=M)R(?=P))'
}



# Monoistopic amino acid residue masses, per
# http://education.expasy.org/student_projects/isotopident/htdocs/aa-list.html
AA_MASSES = {
    'G': 57.02146,
    'A': 71.03711,
    'S': 87.03203, 
    'P': 97.05276,
    'V': 99.06841,
    'T': 101.04768,
    'C': 103.00919,
    'L': 113.08406,
    'I': 113.08406,
    'N': 114.04293,
    'D': 115.02694,
    'Q': 128.05858,
    'K': 128.09496,
    'E': 129.04259,
    'M': 131.04049,
    'H': 137.05891,
    'F': 147.06841,
    'R': 156.10111,
    'Y': 163.06333,
    'W': 186.07931,
}

TRYPSIN_CLEAVAGE_RULE = CLEAVAGE_RULES['trypsin']

DEFAULT_DIGEST_DEFINITION = {
    'protease': {
        'id': 'trypsin',
        'cleavage_rule': TRYPSIN_CLEAVAGE_RULE
    },
    'max_missed_cleavages': 0,
    'min_acids': 6,
}

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.environ.get(
    'PROTEOMICS_DB', '/tmp/testProteomics.db.sqlite')

# secrets.py (if it exists) can override any of the items above.
try:
    from .secrets import *
except:
    pass

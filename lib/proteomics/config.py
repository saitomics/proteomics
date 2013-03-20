TRYPSIN_CLEAVAGE_RULE = '([KR](?=[^P]))|((?<=W)K(?=P))|((?<=M)R(?=P))'

DEFAULT_DIGEST_DEFINITION = {
    'protease': {
        'id': 'trypsin',
        'cleavage_rule': TRYPSIN_CLEAVAGE_RULE
    },
    'max_missed_cleavages': 0,
    'min_acids': 6,
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

from secrets import *

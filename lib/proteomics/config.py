TRYPSIN_CLEAVAGE_RULE = '([KR](?=[^P]))|((?<=W)K(?=P))|((?<=M)R(?=P))'

DEFAULT_DIGEST_DEFINITION = {
    'protease': {
        'id': 'trypsin',
        'cleavage_rule': TRYPSIN_CLEAVAGE_RULE
    },
    'max_missed_cleavages': 0,
    'min_acids': 6,
}

from secrets import *

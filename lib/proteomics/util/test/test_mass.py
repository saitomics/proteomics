import unittest
from proteomics.util import mass


class MassTestCase(unittest.TestCase):
    def test_get_aa_sequence_mass(self):
        aa_sequence = 'ARNDCEQGHILKMFPSTWYV'
        aa_masses = {
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
        actual = mass.get_aa_sequence_mass(aa_sequence, aa_masses=aa_masses)
        expected = 2376.11432
        self.assertEquals(actual, expected)

if __name__ == '__main__':
    unittest.main()

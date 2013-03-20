from proteomics import config
from collections import defaultdict


default_aa_masses = getattr(config, 'AA_MASSES', {})

def get_aa_sequence_mass(sequence, aa_masses=default_aa_masses):
    residue_histogram = defaultdict(int)
    for residue in sequence:
        residue_histogram[residue] += 1
    mass = 0.0
    for residue, count in residue_histogram.items():
        mass += count * aa_masses[residue]
    return mass

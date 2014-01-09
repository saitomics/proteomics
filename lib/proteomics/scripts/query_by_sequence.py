"""
name: query_by_sequence.py

usage: query_by_sequence.py [--max-distance=0] sequence_file 

commissioned by : Dr. Makoto Saito, 2013-03

authorship: adorsk, 2013-05

description: This script queries a peptides database for the given set of
peptide sequences.

Outputs: a CSV document to stdout whose rows contains:
    query_sequence | taxon_id | levenshtein_distance | match_sequence
"""

"""
Imports and setup.
"""
from proteomics import db
from proteomics import config
from proteomics.models import (Peptide, TaxonDigestPeptide, TaxonDigest)
import argparse
import logging
import os
from sqlalchemy.sql import func

"""
Process arguments.
"""
argparser = argparse.ArgumentParser(description=(
    'Query database for peptide sequences'))
argparser.add_argument('--max-distance', type=int, nargs='?', default=0,
                       help=(
                           'List of FASTA files containing protein sequences.'
                       ))
argparser.add_argument('--sequence-file', help=(
    'File containing one amino acid sequence per line.'))

argparser.add_argument('--sequence', help='Amino acid sequence')

"""
Main method.
"""
def main():
    args = argparser.parse_args()

    logger = logging.getLogger('query_by_sequence')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    # Define levenshtein function in SQLite.
    try:
        def levenshtein(s1,s2):
            l1 = len(s1)
            l2 = len(s2)
            matrix = [range(l1 + 1)] * (l2 + 1)
            for zz in range(l2 + 1):
              matrix[zz] = range(zz,zz + l1 + 1)
            for zz in range(0,l2):
              for sz in range(0,l1):
                if s1[sz] == s2[zz]:
                  matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz])
                else:
                  matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1, matrix[zz][sz+1] + 1, matrix[zz][sz] + 1)
            return matrix[l2][l1]

        connection = db.get_connection()
        connection.connection.create_function("LEVENSHTEIN", 2, levenshtein)
    except Exception as e:
        logger.exception('Could not define Levenshtein distance function: %s' % e)
        raise e

    session = db.get_session(bind=connection)

    # Read in sequences to query.
    sequences = []
    if args.sequence_file:
        with open(args.sequence_file, 'rb') as f:
            sequences = [line.strip() for line in f.readlines()]
    elif args.sequence:
        sequences = [args.sequence]

    if not sequences:
        argparser.error("Provide a query sequence via the '--sequence' option, "
                        "or a set of sequences via the --sequence-file option")

    # Print headers. 
    headers = ['query', 'taxon', 'lev_distance', 'match']
    print ','.join(headers)

    # Execute query for each sequence and print results.
    for seq in sequences:
        lev_dist = func.LEVENSHTEIN(Peptide.sequence, seq)
        q = (session.query(TaxonDigest.taxon_id, lev_dist,
                           Peptide.sequence)
             .select_from(Peptide)
             .join(TaxonDigestPeptide)
             .join(TaxonDigest)
             .filter(lev_dist <= args.max_distance)
            )
        for row in q:
            print ','.join([str(s) for s in [seq] + list(row)])

if __name__ == '__main__':
    main()

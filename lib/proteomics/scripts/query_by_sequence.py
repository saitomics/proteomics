"""
name: query_by_sequence.py

usage: query_by_sequence.py [--max-distance=0] sequence_file 

commissioned by : Dr. Makoto Saito, 2013-03

authorship: adorsk, 2013-05

description: This script queries a peptides database for the given set of
peptide sequences.
Assumptions:
    - The 'SQLITE_LEVENSHTEIN' environment variable is set to the path to the
    sqlite levenshtein extension.
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

argparser.add_argument('sequence', nargs='?', help='Amino acid sequence')

"""
Main method.
"""
def main():
    args = argparser.parse_args()

    logger = logging.getLogger('query_by_sequence')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    # Load Sqlite levenshtein extension.
    try:
        connection = db.get_connection()
        connection.connection.enable_load_extension(True)
        connection.execute("SELECT load_extension('%s')" % (
            os.environ['SQLITE_LEVENSHTEIN']))
    except Exception as e:
        logger.exception('Could not load Sqlite Levenshtein extension. '
                         'SQLITE_LEVENSHTEIN environment variable must contain '
                         'path to levenshtein extension.')
        raise e

    session = db.get_session(bind=connection)

    # Read in sequences to query.
    sequences = []
    if args.sequence_file:
        with open(args.sequence_file, 'rb') as f:
            sequences = [line.strip() for line in f.readlines()]
    elif args.sequence:
        sequences = [args.sequence]

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

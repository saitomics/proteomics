"""
name: generate_redundancy_tables.py

commissioned by : Dr. Makoto Saito, 2013-03

authorship: adorsk, 2013-03

description: This script generates redundancy tables for a given set of taxon
digests.

Assumptions:
    - The redundancy db has already been created and is readable.
"""

"""
Imports and setup.
"""
from proteomics import config
from proteomics import db
from proteomics.models import (Taxon, Protease, Digest, TaxonDigest)
from proteomics.services import redundancy
import argparse
import logging
import csv
import os


"""
Process arguments.
"""
argparser = argparse.ArgumentParser(description=(
    'Generate redundancy tables for the given taxon digests.'))
argparser.add_argument('--taxon-id-file', help=(
    'A file containing a list of taxon IDs to include in the redundancy table,'
    ' one taxon id per line. The default digest will be used to search for'
    'TaxonDigests.'))
argparser.add_argument('--taxon-ids', nargs='*', help=(
    'List of taxon IDs to include in the redundancy table. The default digest'
    ' will be used to search for TaxonDigests. This option will override the'
    ' --taxons-file option.'))
argparser.add_argument('--output-dir', required=True, help=(
    'Output directory. CSV tables will be written to this directory.'))

"""
Main method.
"""
def main():
    args = argparser.parse_args()

    logger = logging.getLogger('redundancy_tables')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    # Check that taxon ids or taxon id file were provided.
    if not (args.taxon_ids or args.taxon_id_file):
        raise Exception("Must provide --taxon-ids or --taxon-id-file option")

    session = db.get_session()

    # Get taxons.
    if args.taxon_ids:
        taxon_ids = args.taxon_ids
    else:
        with open(args.taxon_id_file, 'rb') as f:
            taxon_ids = [row[0] for row in csv.reader(f)]

    # Get the digest.
    digest = get_digest(logger, config.DEFAULT_DIGEST_DEFINITION, session)

    # Get the TaxonDigests.
    taxon_digests = (
        session.query(TaxonDigest)
        .filter(TaxonDigest.digest == digest)
        .join(Taxon)
        .filter(Taxon.id.in_(taxon_ids))
    ).all()

    # Generate the redundancy tables.
    tables = redundancy.generate_redundancy_tables(
        session, taxon_digests, logger=logger)

    # Create output dir if it does not exist.
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Output tables.
    for table_id, table in tables.items():
        table_file = os.path.join(args.output_dir, table_id + '.csv')
        logger.info("Writing '%s'..." % table_file)
        with open(table_file, 'wb') as f:
            w = csv.writer(f)
            for row in table:
                w.writerow(row)

    logger.info("Done.")


""" Helper methods. """
def get_digest(logger, digest_def, session=None):
    """ Get digest from a digest definition."""
    if not session:
        session = db.get_session()

    # Get protease object.
    protease = session.query(Protease).get(
        digest_def['protease']['id'])
    if not protease:
        raise Exception("No protease exists for the given definition.")

    # Get digest object.
    digest = (
        session.query(Digest)
        .filter(Digest.protease == protease)
        .filter(Digest.max_missed_cleavages == digest_def.get(
            'max_missed_cleavages'))
        .filter(Digest.min_acids == digest_def.get(
            'min_acids'))
        .filter(Digest.max_acids == digest_def.get(
            'max_acids'))
    ).first()
    if not digest:
        raise Exception("No digest exists for the given definition.")

    return digest

if __name__ == '__main__':
    main()

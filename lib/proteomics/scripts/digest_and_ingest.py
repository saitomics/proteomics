"""
name: digest_and_ingest.py

usage: digest_and_ingest.py [--digest-config=digest_config_file] fasta1 fasta2 ...

commissioned by : Dr. Makoto Saito, 2013-03

authorship: adorsk, 2013-03

description: This script digests peptides from protein sequences stored in
FASTA files. 
Assumptions:
    - Each FASTA file is assumed to contain the proteome for one taxon.
    - FASTA file names contain the taxon id e.g. 'syn5802.fasta'.
    - The redundancy db has already been created and is writeable.
"""

"""
Imports and setup.
"""
from proteomics import db
from proteomics import config
from proteomics.models import (Protease, Digest)
from proteomics.services.digest_and_ingest import DigestAndIngestTask
import argparse
import logging
import json

"""
Process arguments.
"""
argparser = argparse.ArgumentParser(description=(
    'Digest and ingest peptides from FASTA protein sequence files.'))
argparser.add_argument('--digest-def', help=(
    'JSON file containing a digest definition. If not provided, default digest'
    'will be used'))
argparser.add_argument('fasta_files', nargs='+',
                    help=('List of FASTA files containing protein sequences.'))
"""
Main method.
"""
def main():
    args = argparser.parse_args()

    logger = logging.getLogger('digest_and_ingest')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    fasta_files = args.fasta_files

    # Parse digest definition if given.
    if args.digest_def:
        try:
            digest_def = json.loads(args.digest_def)
        except:
            logger.exception("Could not parse digest_def file '%s'" % (
                args.digest_def))
    # Otherwise use default digest.
    else:
        digest_def = config.DEFAULT_DIGEST_DEFINITION

    # Get or create the digest.
    digest = get_digest(logger, digest_def)

    # Run the digest/ingest task.
    task = DigestAndIngestTask(
        logger=logger,
        fasta_paths=fasta_files,
        digest=digest,
        get_connection=db.get_connection,
    )
    stats = task.run()
    logger.info("Statistics on records created: %s" % stats)

""" Helper methods. """
def get_digest(logger, digest_def):
    """ Fetch or create a digest from a digest definition."""
    session = db.get_session()

    # Get or create protease.
    protease = session.query(Protease).get(
        digest_def['protease']['id'])
    if not protease:
        logger.info(
            "No protease exists for the given definition, creating...")
        protease = Protease(**digest_def['protease'])
        session.add(protease)
    # Get or create digest object.
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
        logger.info(
            "No digest exists for the given definition, creating...")
        digest_kwargs = {}
        digest_kwargs.update(digest_def)
        digest_kwargs['protease'] = protease
        digest = Digest(**digest_kwargs)
        session.add(digest)
    session.commit()
    return digest

if __name__ == '__main__':
    main()

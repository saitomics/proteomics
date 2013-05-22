"""
name: clear_taxon_data.py

usage: clear_taxon_data.py [--taxon-ids-file=taxon_ids_file] [--taxon-ids= id1 id2 ..]

commissioned by : Dr. Makoto Saito, 2013-03

authorship: adorsk, 2013-05

description: This script clears data in the redundancy DB for a given set of taxon ids.
Assumptions:
    - The redundancy db has already been created and is writeable.
"""

"""
Imports and setup.
"""
from proteomics import db
from proteomics import config
from proteomics.models import (Protease, Digest)
from proteomics.services.clear_taxon_data import ClearTaxonDataTask
import argparse
import logging
import json

"""
Process arguments.
"""
argparser = argparse.ArgumentParser(description=(
    'Clear data in the DB for the given Taxons.'))
argparser.add_argument('--taxon-ids-file', help=(
    'File containing a list of taxon ids to clear, one id per line'))
argparser.add_argument('--taxon-ids', nargs='*', help=(
    'List of taxon ids to clear.'))
"""
Main method.
"""
def main():
    args = argparser.parse_args()

    logger = logging.getLogger('digest_and_ingest')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    if args.taxon_ids_file:
        with open(args.taxon_ids_file) as f:
            taxon_ids = f.readlines()
    else:
        taxon_ids = args.taxon_ids

    if not taxon_ids:
        logger.error("No taxon ids were given, exiting.")
        exit()

    # Confirm deletion w/ the user.
    print "You are about to delete the following taxons:\n"
    print "\n".join(taxon_ids), "\n"
    confirmation = raw_input("Type 'yes' and hit enter if this is really "
                             "what you want to do: ")
    if confirmation != 'yes':
        logger.info("You did not enter 'yes', quitting. Nothing has been done.")
        exit()

    # Run the clearing task.
    task = ClearTaxonDataTask(
        logger=logger,
        taxon_ids=taxon_ids,
        get_connection=db.get_connection,
    )
    task.run()
    logger.info("Done.")

if __name__ == '__main__':
    main()

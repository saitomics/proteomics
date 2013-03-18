from proteomics.models import (TaxonDigestPeptide, TaxonDigest, Peptide)
from sqlalchemy.sql import func
import itertools
import logging


def count_common_peptides(session=None, taxon_digests=[]):
    if not taxon_digests:
        return
    taxon_digest_ids = [taxon_digest.id for taxon_digest in taxon_digests]
    taxon_digest_count = func.count(TaxonDigest.id)
    q = (
        session.query(taxon_digest_count, Peptide.id)
        .select_from(TaxonDigestPeptide)
        .join(TaxonDigest)
        .join(Peptide)
        .filter(TaxonDigest.id.in_(taxon_digest_ids))
        .group_by(Peptide.id)
        .having(taxon_digest_count == len(taxon_digests))
    )
    return q.count()

def generate_redundancy_table(session=None, taxon_digests=[], logger=None):
    if not logger:
        logger = logging.getLogger()

    # Initialize redundancy table.
    redundancies = {}
    combinations = itertools.combinations(taxon_digests, 2)
    for combo in combinations:
        logger.info("Counting peptides in common for %s" % (str([
            "(taxon: %s, digest: %s)" % (
                taxon_digest.taxon.id, taxon_digest.digest.id
            ) for taxon_digest in combo])))
        redundancies[combo] = count_common_peptides(session, combo)

    # Format redundancy table, sorting by taxon ids.
    # We only put values in the upper-right portion.
    redundancy_table = []
    sorted_taxon_digests = sorted(taxon_digests, key=lambda td: td.taxon.id)
    # Top row.
    redundancy_table.append([None] + [td.taxon.id for td in
                                      sorted_taxon_digests])
    # Data rows.
    for i, td1 in enumerate(sorted_taxon_digests):
        data_row = [td1.taxon.id]
        for j, td2 in enumerate(sorted_taxon_digests):
            if j < i:
                data_row.append(None)
            elif j == i:
                data_row.append('X')
            else:
                value = redundancies.get((td1,td2,))
                # Key might be in another order.
                if not value:
                    value = redundancies.get((td2,td1,))
                data_row.append(value)
        redundancy_table.append(data_row)
    return redundancy_table

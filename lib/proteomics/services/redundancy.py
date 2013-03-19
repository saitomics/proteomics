from proteomics.models import (TaxonDigestPeptide, TaxonDigest, Peptide)
from sqlalchemy.sql import func
import itertools
import logging


def count_common_peptides(session=None, taxon_digests=[]):
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

def count_peptide_union(session=None, taxon_digests=[]):
    taxon_digest_ids = [taxon_digest.id for taxon_digest in taxon_digests]
    q = (
        session.query(TaxonDigestPeptide)
        .join(TaxonDigest)
        .filter(TaxonDigest.id.in_(taxon_digest_ids))
    )
    return q.count()

def generate_redundancy_tables(session=None, taxon_digests=[], logger=None):
    """ 
    Generates tables of:
        - counts: counts of peptides in common between pairs of taxon digests
        - percents: counts/(sum of peptides for the pair)
    """

    if not logger:
        logger = logging.getLogger()

    # Generate pairs.
    combinations = itertools.combinations(taxon_digests, 2)

    # Get redundancies and sums by querying db.
    # Calculate percents.
    values = {
        'counts': {},
        'percents': {},
    }
    redundancies = {}
    percents = {}
    for combo in combinations:
        logger.info("Counting peptides in common for %s" % (str([
            "(taxon: %s, digest: %s)" % (
                taxon_digest.taxon.id, taxon_digest.digest.id
            ) for taxon_digest in combo])))
        num_in_common = count_common_peptides(session, combo)
        num_in_union = count_peptide_union(session, combo)
        if num_in_union:
            percent_in_common = 100.0 * num_in_common/num_in_union
        else:
            percent_in_common = 0
        values['counts'][combo] = num_in_common
        values['percents'][combo] = percent_in_common

    # Assemble tables, sorting by taxon ids.
    # We only put values in the upper-right portion.
    tables = {
        'counts': [],
        'percents': []
    }
    sorted_taxon_digests = sorted(taxon_digests, key=lambda td: td.taxon.id)

    for table_id, table in tables.items():
        # Top row.
        table.append([None] + [td.taxon.id for td in sorted_taxon_digests])
        # Data rows.
        for i, td1 in enumerate(sorted_taxon_digests):
            data_row = [td1.taxon.id]
            for j, td2 in enumerate(sorted_taxon_digests):
                if j < i:
                    data_row.append(None)
                elif j == i:
                    data_row.append('X')
                else:
                    value = values[table_id].get((td1,td2,))
                    # Key might be in another order.
                    if not value:
                        value = values[table_id].get((td2,td1,))
                    data_row.append(value)
            table.append(data_row)

    return tables

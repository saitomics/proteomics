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
        session.query(Peptide.id)
        .join(TaxonDigestPeptide)
        .join(TaxonDigest)
        .filter(TaxonDigest.id.in_(taxon_digest_ids))
        .group_by(Peptide.id)
    )
    return q.count()

def generate_redundancy_tables(session=None, taxon_digests=[], logger=None):
    """ 
    Generates tables of:
        - counts: counts of peptides in common between pairs of taxon digests
        - union percents: |td1 ^ td2|/|td1 + td2|
        - pairwise percents: |td1 ^ td2|/|td1|
    """

    if not logger:
        logger = logging.getLogger()

    # Generate pairs.
    combinations = [c for c in itertools.combinations(taxon_digests, 2)]

    # Get redundancies and sums by querying db.
    # Calculate percents.
    values = {
        'intersection_counts': {},
        'union_percents': {},
        'individual_percents': {},
        'individual_counts': {},
    }
    redundancies = {}
    percents = {}
    for combo in combinations:
        logger.info("Counting peptides in common for %s" % (str([
            "(taxon: %s, digest: %s)" % (
                taxon_digest.taxon.id, taxon_digest.digest.id
            ) for taxon_digest in combo])))
        # Sorted combo for keying.
        combo_key = get_td_combo_key(combo)
        # Get intersection counts and union percentages.
        num_in_intersection = count_common_peptides(session, combo)
        num_in_union = count_peptide_union(session, combo)
        if num_in_union:
            percent_in_common = 100.0 * num_in_intersection/num_in_union
        else:
            percent_in_common = 0
        values['intersection_counts'][combo_key] = num_in_intersection
        values['union_percents'][combo_key] = percent_in_common
        # Get individual counts and percentages.
        for td in combo:
            if td not in values['individual_counts']:
                values['individual_counts'][td] = count_common_peptides(
                    session, [td])
            num_in_td = values['individual_counts'][td]
            if num_in_td:
                values['individual_percents'][(td,combo_key,)] = \
                        100.0 * num_in_intersection/num_in_td

    # Sort taxon digests.
    sorted_taxon_digests = sorted(taxon_digests, key=lambda td: td.taxon.id)

    # Assemble tables.
    tables = {
        'intersection_counts': [],
        'union_percents': [],
        'individual_percents': [],
        'individual_counts': []
    }

    # Assemble individual counts table.
    for i, td in enumerate(sorted_taxon_digests):
        label = "|%s|" % td.taxon.id
        value = values['individual_counts'][td]
        tables['individual_counts'].append([label, value])

    # Assemble intersection_count and union_pct tables.
    # These tables have one row per combination.
    for td1, td2 in combinations:
        combo_key = get_td_combo_key((td1,td2,))
        # Intersection count.
        intersection_label = '|%s ^ %s|' % (td1.taxon.id, td2.taxon.id)
        intersection_count = values['intersection_counts'][combo_key]
        tables['intersection_counts'].append(
            [intersection_label, intersection_count])
        # Union percents.
        union_label = '|%s U %s|' % (td1.taxon.id, td2.taxon.id)
        union_pct_label = "%s/%s" % (intersection_label, union_label)
        union_pct = values['union_percents'][combo_key]
        tables['union_percents'].append([union_pct_label, union_pct])

    # Assemble individual percents table.
    # This table has one row per permutation.
    for i, td1 in enumerate(sorted_taxon_digests):
        for j, td2 in enumerate(sorted_taxon_digests):
            combo_key = get_td_combo_key((td1,td2,))
            pct_key = (td1,combo_key,)
            if pct_key in values['individual_percents']:
                label = "|%s ^ %s|/|%s|" % (td1.taxon.id, td2.taxon.id,
                                            td1.taxon.id)
                value = values['individual_percents'][pct_key]
                tables['individual_percents'].append([label, value])

    return tables

def get_td_combo_key(td_combo):
    """ Get a key for a taxon digest combo."""
    return tuple(sorted(td_combo, key=lambda td: td.taxon.id))

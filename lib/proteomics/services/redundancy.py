from proteomics.models import (TaxonDigestPeptide, TaxonDigest, Peptide)
from sqlalchemy.sql import func


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

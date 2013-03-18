import unittest
from proteomics import db
from proteomics.models import (Digest, Taxon, TaxonDigest, Peptide, 
                               TaxonDigestPeptide)
from proteomics.services import redundancy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import itertools
import tempfile
import os
import logging


class RedundancyTestCase(unittest.TestCase):
    def setUp(self):

        # Setup DB.
        self.engine = create_engine('sqlite://')
        def get_connection():
            return self.engine.connect()
        self.get_connection = get_connection
        db.metadata.create_all(bind=self.engine)
        self.connection = self.get_connection()
        self.session = sessionmaker(bind=self.connection)()

        # Setup mock data.
        taxons = []
        for t in range(1, 3+1):
            taxons.append(Taxon(id=t))
        self.session.add_all(taxons)

        digests = []
        for d in range(1,1+1):
            digests.append(Digest(id=1))
        self.session.add_all(digests)

        taxon_digests = []
        taxon_digest_counter = 0
        for d in digests:
            for t in taxons:
                taxon_digest_counter += 1
                taxon_digests.append(TaxonDigest(id=taxon_digest_counter, 
                                                 taxon=t, digest=d))
        self.session.add_all(taxon_digests)

        peptides = []
        for p in range(1, 12+1):
            peptides.append(Peptide(id=p))
        self.session.add_all(peptides)

        # A peptide is assigned to a taxon digest if the peptide's
        # id is a factor of the taxon_digest's id.
        taxon_digest_peptides = []
        for taxon_digest in taxon_digests:
            for peptide in peptides:
                if (peptide.id % taxon_digest.id) == 0:
                    taxon_digest_peptides.append(TaxonDigestPeptide(
                        taxon_digest=taxon_digest,
                        peptide=peptide
                    ))
        self.session.add_all(taxon_digest_peptides)
        self.session.commit()

    def test_count_common_peptides(self):
        connection = self.get_connection()
        session = sessionmaker(bind=connection)()
        taxon_digests = session.query(TaxonDigest).all()
        pairs = itertools.combinations(taxon_digests, 2)
        triples = itertools.combinations(taxon_digests, 3)
        actual = {}
        for combination in itertools.chain(pairs, triples):
            ids = tuple([item.id for item in combination])
            actual[ids] = redundancy.count_common_peptides(
                session=session,
                taxon_digests=combination
            )
        expected = {(1, 2): 6, (1, 3): 4, (2, 3): 2, (1, 2, 3): 2}
        self.assertEquals(expected, actual)

    def test_generate_redundancy_tables(self):
        taxon_digests = self.session.query(TaxonDigest).all()
        actual = redundancy.generate_redundancy_tables(
            session=self.session,
            taxon_digests=taxon_digests
        )

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()

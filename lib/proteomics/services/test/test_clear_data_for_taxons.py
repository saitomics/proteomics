import unittest
from proteomics import db
from proteomics.models import (Protease, Digest, TaxonDigest, 
                               TaxonDigestPeptide, TaxonProtein, Taxon)
from proteomics.services.digest_and_ingest import DigestAndIngestTask
from proteomics.services.clear_taxon_data import ClearTaxonDataTask
from proteomics.config import CLEAVAGE_RULES as expasy_rules
from sqlalchemy import create_engine
import tempfile
import os
import logging


class ClearTaxonDataTaskTestCase(unittest.TestCase):
    def setUp(self):

        # Setup DB.
        #d = tempfile.mkdtemp(prefix="tdb.")
        #db_file = os.path.join(d, "foo")
        #self.engine = create_engine('sqlite:///%s' % db_file)
        self.engine = create_engine('sqlite://')
        def get_connection():
            return self.engine.connect()
        self.get_connection = get_connection
        db.metadata.create_all(bind=self.engine)

        self.session = db.get_session(bind=self.get_connection())

        # Create trypsin protease.
        trypsin = Protease(id='trypsin', cleavage_rule=expasy_rules['trypsin'])
        self.session.add(trypsin)

        # Create digest.
        self.digest = Digest(protease=trypsin)
        self.session.add(self.digest)
        self.session.commit()

        # Create mock FASTA file.
        hndl, self.fasta_file = tempfile.mkstemp(suffix=".fasta")
        self.taxon_id = os.path.splitext(os.path.basename(self.fasta_file))[0]
        with open(self.fasta_file, 'wb') as fh:
            fh.write(self.get_mock_fasta())

    def test_clear_data_for_taxons(self):
        logger = logging.getLogger('testLogger')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.INFO)

        ingest_task = DigestAndIngestTask(
            logger=logger,
            fasta_paths=[self.fasta_file],
            digest=self.digest,
            get_connection=self.get_connection
        )
        ingest_task.run()

        assert self.session.query(TaxonDigestPeptide).count() == 98
        assert self.session.query(TaxonDigest).count() == 1
        assert self.session.query(TaxonProtein).count() == 4
        assert self.session.query(Taxon).count() == 1

        clear_task = ClearTaxonDataTask(
            logger=logger,
            get_connection=self.get_connection,
            taxon_ids=[self.taxon_id]
        )
        clear_task.run()

        assert self.session.query(TaxonDigestPeptide).count() == 0
        assert self.session.query(TaxonDigest).count() == 0
        assert self.session.query(TaxonProtein).count() == 0
        assert self.session.query(Taxon).count() == 0

    def tearDown(self):
        os.remove(self.fasta_file)

    def get_mock_fasta(self):
        return """
>638957745 ZP_01083369 WH5701_03745 putative glutamate synthetase [Synechococcus sp. WH 5701]
MNLEEGKDYFYCACGRSSDQPFCDGSHEGSGFTPLAFVAERGGKALLCRC
KQTATPPYCDGTHTRVPADRVGTTFSVDADGEGDGTEEGDGNDADPEEPD
HHGMPEPRATAEEPNLELIHQLAEHGLDRMGAEGPVAAMGVPRSLLPLWD
DIQILTAQLARRPLAGDAAVGTELVIGPRARRPLRLEIPLLVSDMSFGAL
SEEAKQALATGAERAGTGICSGEGGMLPEEQAANHRYLYELAPAMFGYRE
EVLSQVQAFHFKAGQAAKTGTGSHLPGAKVTARIAEIRGIPEGQPSCSPA
VFSDLHSPADFRAFGDRVRELSGGIPVGMKLSAQHIEHDLDFALEAGVDY
LILDGRGGGTGGAPLLFRDHIAVPTIPALARARAHLDRSGVGGQVTLIVT
GGLRTPADCIKALALGADGVALANAAIQAIGCVGSRICHTNRCPAGVATQ
DPQLRRRLEVEHAALRLERFLRATVALMQVMARACGHDHLGRLRREDLAS
WHRDLAELAGIAWSGRSRCQLARSSRRSRPR

>638957746 ZP_01083370 WH5701_03750 ABC transporter for sugars, solute-binding protein [Synechococcus sp. WH 5701]
MGLRSTLRYAALALLLVGLIVSGGLRAQRQEPVIVTALMPAPFAEATAPI
VERFNRRHPGIELRVNRGPFETEAISDLAISSLLLGDSPYDLLLMDVTWT
PKYAAAGWLAPLEPLLGEDALAGVVPGAREGNRFDGHLWRIPLVADMGLL
YWRTDLMAAPPRTPDELMATAGALQRAGRVRWGYVWQGRQYEGLSCVFLE
VLRGFGGQWLSASADRVELGSPAGVAAASWLRQLIDLGITPRAVANFAEP
EALQSFEAGDAALMRNWPYAWAELQKPGSQVRGKVGVTTMVAAPGGSPAA
TQGSWGFSLVSQSPHPREAALVIAALTAPGVQKDLARRLGYTPTLSALFE
DPELVAANPVLPELRRALEATVLRPLSPLYAQLSDILQRQLSEVITGERE
PAEGMERAQRLSNQLLRASGVGASGVEARS

>638957747 ZP_01083371 WH5701_03755 ABC transporter for possibly for trehalose/maltose, membrane component [Synechococcus sp. WH 5701]
MTLLLTLPALLLLALVFAVPLLRYGWLSFHADSVITGLQPVPNGGANWLR
LIEDERFWQDTVQTLRFAGLSVALELLLGLALALLLHQSWRGRTAVRTIT
LLPWALPTAVMALGWRWIFNDPYGPINALVQALGLPALPFLSSPASTWLV
VVLADVWKTTPFVALLLLAGLQSIPTDLYEAFALEGGTSAQALRQITLPL
LLPYAFLAVLFRLAQALGVFDLVQILTGGGPAGSTETLALYSYLSAMRFL
DFGYSATVMLGMFVLLLGLTAALLLGRRWLAGGRS

>DUPLICATE_OF_638957745 ZP_01083369 WH5701_03745 putative glutamate synthetase [Synechococcus sp. WH 5701]
MNLEEGKDYFYCACGRSSDQPFCDGSHEGSGFTPLAFVAERGGKALLCRC
KQTATPPYCDGTHTRVPADRVGTTFSVDADGEGDGTEEGDGNDADPEEPD
HHGMPEPRATAEEPNLELIHQLAEHGLDRMGAEGPVAAMGVPRSLLPLWD
DIQILTAQLARRPLAGDAAVGTELVIGPRARRPLRLEIPLLVSDMSFGAL
SEEAKQALATGAERAGTGICSGEGGMLPEEQAANHRYLYELAPAMFGYRE
EVLSQVQAFHFKAGQAAKTGTGSHLPGAKVTARIAEIRGIPEGQPSCSPA
VFSDLHSPADFRAFGDRVRELSGGIPVGMKLSAQHIEHDLDFALEAGVDY
LILDGRGGGTGGAPLLFRDHIAVPTIPALARARAHLDRSGVGGQVTLIVT
GGLRTPADCIKALALGADGVALANAAIQAIGCVGSRICHTNRCPAGVATQ
DPQLRRRLEVEHAALRLERFLRATVALMQVMARACGHDHLGRLRREDLAS
WHRDLAELAGIAWSGRSRCQLARSSRRSRPR
"""

if __name__ == '__main__':
    unittest.main()

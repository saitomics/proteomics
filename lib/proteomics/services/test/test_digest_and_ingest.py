import unittest
from proteomics import db
from proteomics.models import Protease, Digest
from proteomics.services.digest_and_ingest import DigestAndIngestTask
from pyteomics.parser import expasy_rules
from sqlalchemy import create_engine
import tempfile
import os
import logging


class IngestAndDigestTestCase(unittest.TestCase):
    def setUp(self):

        # Setup DB.
        d = tempfile.mkdtemp(prefix="tdb.")
        db_file = os.path.join(d, "foo")
        self.engine = create_engine('sqlite:///%s' % db_file)
        #self.engine = create_engine('sqlite://')
        def get_connection():
            return self.engine.connect()
        self.get_connection = get_connection
        db.metadata.create_all(bind=self.engine)

        session = db.get_session(bind=self.get_connection())

        # Create trypsin protease.
        trypsin = Protease(id='trypsin', cleavage_rule=expasy_rules['trypsin'])
        session.add(trypsin)

        # Create digest.
        self.digest = Digest(protease=trypsin)
        session.add(self.digest)
        session.commit()


        # Create mock FASTA file.
        hndl, self.fasta_file = tempfile.mkstemp(prefix="tst.fasta.")
        with open(self.fasta_file, 'wb') as fh:
            fh.write(self.get_mock_fasta())

    def test_ingest_and_digest(self):
        logger = logging.getLogger('testLogger')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.INFO)

        task = DigestAndIngestTask(
            logger=logger,
            fasta_paths=[self.fasta_file],
            #fasta_paths=[
                #'/home/adorsk/projects/saitomics/data/syn5701.fasta',
                #'/home/adorsk/projects/saitomics/data/syn7803.fasta'
            #],
            digest=self.digest,
            get_connection=self.get_connection
        )
        stats = task.run()

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

import unittest
from proteomics import db
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


class DBTestCase(unittest.TestCase):

    def get_engine_uri(self):
        return 'sqlite://'

    def setUp(self, refresh_db=True):
        self.engine = create_engine(self.get_engine_uri())
        self.connection = self.engine.connect()
        self.trans = self.connection.begin()

        db.session = scoped_session(sessionmaker(bind=self.connection))

        if refresh_db:
            self.refresh_db(bind=self.connection)

    def refresh_db(self, bind=None):
        db.clear_db(bind=bind)
        db.init_db(bind=bind)

    def tearDown(self):
        self.trans.rollback()
        db.session.close

if __name__ == '__main__':
    unittest.main()

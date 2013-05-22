from proteomics.models import (Taxon, Protein, 
                               TaxonProtein, ProteinDigest, Peptide, 
                               ProteinDigestPeptide, TaxonDigestPeptide, 
                               TaxonDigest, Digest, Protease)
from proteomics import db
from proteomics.util.logging_util import LoggerLogHandler
import os
import logging
from sqlalchemy.orm import sessionmaker
from collections import defaultdict


class ClearTaxonDataTask(object):
    def __init__(self, logger=logging.getLogger(), taxon_ids=[], 
                 get_connection=None, **kwargs):
        self.logger = logger
        self.taxon_ids = taxon_ids

        # Assign get_connection function.
        if not get_connection:
            def get_connection():
                engine = create_engine('sqlite://')
                return engine.connect()
        self.get_connection = get_connection

    def run(self):
        # Get session.
        self.session = db.get_session(bind=self.get_connection())

        taxons = (
            self.session.query(Taxon)
            .filter(Taxon.id.in_(self.taxon_ids))
        )

        for taxon in taxons:
            self.logger.info("Clearing data for taxon '%s'" % taxon.id)
            self.clear_data_for_taxon(taxon)

    def clear_data_for_taxon(self, taxon):

        # Get TaxonDigests.
        taxon_digests = (
            self.session.query(TaxonDigest)
            .join(Taxon)
            .filter(Taxon.id == taxon.id)
        )

        # Delete TaxonDigestPeptides and TaxonDigests
        for td in taxon_digests:
            (
                self.session.query(TaxonDigestPeptide)
                .filter(TaxonDigestPeptide.taxon_digest_id == td.id)
                .delete()
            )
            self.session.delete(td)

        # Delete TaxonProteins.
        (
            self.session.query(TaxonProtein)
            .filter(TaxonProtein.taxon_id == taxon.id)
            .delete()
        )

        # Delete Taxon
        self.session.query(Taxon).filter(Taxon.id == taxon.id).delete()

        # Commit the deletes.
        self.session.commit()

    def get_child_logger(self, name=None, base_msg=None, parent_logger=None):
        if not parent_logger:
            parent_logger = self.logger
        logger = logging.getLogger("%s_%s" % (id(self), name))
        formatter = logging.Formatter(base_msg + ' %(message)s.')
        log_handler = LoggerLogHandler(parent_logger)
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)
        logger.setLevel(parent_logger.level)
        return logger

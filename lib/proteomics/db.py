"""
Proteomics DB.
The goal of the db schema is to make proteomics data ingesta and analysis
modular, flexible, and fast.
"""


from proteomics import models
from proteomics import config
from sqlalchemy import (MetaData, Table, Column, Integer, String, ForeignKey,
                       DateTime, Float)
from sqlalchemy.orm import mapper, relationship
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import object_session 
from sqlalchemy.orm.util import has_identity 

engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
session = scoped_session(sessionmaker(bind=engine))

def get_session():
    return session()

def init_db(bind=engine):
    metadata.create_all(bind=bind, checkfirst=True)

def clear_db(bind=engine):
    metadata.drop_all(bind=bind)

def get_session_w_external_trans(orig_session):
    con = orig_session.bind.connect()
    trans = con.begin()
    new_session = sessionmaker()(bind=con)
    return con, trans, new_session

def get_obj_state(obj):
    if object_session(obj) is None and not has_identity(obj):
        return 'transient'
    elif object_session(obj) is not None and not has_identity(obj):
        return 'pending'
    elif object_session(obj) is None and has_identity(obj):
        return 'detached'
    elif object_session(obj) is not None and has_identity(obj):
        return 'persistent'


# Define tables.
metadata = MetaData()

tables = {}

tables['File'] = Table(
    'files', metadata,
    Column('id', String, primary_key=True),
    Column('basename', String),
)
mapper(models.File, tables['File'])

tables['FileDigest'] = Table(
    'files_digests', metadata,
    Column('file_id', String, ForeignKey('files.id'), primary_key=True),
    Column('digest_id', Integer, ForeignKey('digests.id'), primary_key=True),
)
mapper(models.FileDigest, tables['FileDigest'], properties={
    'file': relationship(models.File),
    'digest': relationship(models.Digest)
})

tables['Taxon'] = Table(
    'taxons', metadata,
    Column('id', String, primary_key=True),
)
mapper(models.Taxon, tables['Taxon'])

tables['TaxonDigest'] = Table(
    'taxons_digests', metadata,
    Column('taxon_id', String, ForeignKey('taxons.id'), primary_key=True),
    Column('digest_id', Integer, ForeignKey('digests.id'), primary_key=True),
)
mapper(models.TaxonDigest, tables['TaxonDigest'], properties={
    'taxon': relationship(models.Taxon),
    'digest': relationship(models.Digest)
})

tables['Protein'] = Table(
    'proteins', metadata,
    Column('id', Integer, primary_key=True),
    Column('sequence', String, index=True),
    Column('mass', Float),
)
mapper(models.Protein, tables['Protein'])

tables['ProteinDigest'] = Table(
    'proteins_digests', metadata,
    Column('protein_id', String, ForeignKey('proteins.id'), primary_key=True),
    Column('digest_id', Integer, ForeignKey('digests.id'), primary_key=True),
)
mapper(models.ProteinDigest, tables['ProteinDigest'], properties={
    'protein': relationship(models.Protein),
    'digest': relationship(models.Digest)
})

tables['ProteinInstance'] = Table(
    'protein_instances', metadata,
    Column('id', Integer, primary_key=True),
    Column('protein_id', Integer, ForeignKey('proteins.id'), index=True),
    Column('taxon_id', String, ForeignKey('taxons.id'), index=True),
    Column('metadata', String),
)
mapper(models.ProteinInstance, tables['ProteinInstance'], properties={
    'protein': relationship(models.Protein),
    'taxon': relationship(models.Taxon),
})

tables['Peptide'] = Table(
    'peptides', metadata,
    Column('id', Integer, primary_key=True),
    Column('sequence', String, index=True),
    Column('mass', Float),
)
mapper(models.Peptide, tables['Peptide'])

tables['PeptideInstance'] = Table(
    'peptide_instances', metadata,
    Column('id', Integer, primary_key=True),
    Column('peptide_id', Integer, ForeignKey('peptides.id'), index=True),
    Column('digest_id', Integer, ForeignKey('digests.id'), index=True),
    Column('protein_id', Integer, ForeignKey('proteins.id'), index=True),
    Column('metadata', String),
)
mapper(models.PeptideInstance, tables['PeptideInstance'], properties={
    'peptide': relationship(models.Peptide),
    'digest': relationship(models.Digest),
    'protein': relationship(models.Protein),
})

tables['Protease'] = Table(
    'proteases', metadata,
    Column('id', String, primary_key=True),
    Column('cleavage_rule', String),
)
mapper(models.Protease, tables['Protease'])

tables['Digest'] = Table(
    'digests', metadata,
    Column('id', Integer, primary_key=True),
    Column('protease_id', String, ForeignKey('proteases.id')),
    Column('max_missed_cleavages', Integer),
)
mapper(models.Digest, tables['Digest'], properties={
    'protease': relationship(models.Protease),
})

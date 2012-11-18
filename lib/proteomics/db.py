"""
Proteomics DB.
The goal of the db schema is to make proteomics data ingesta and analysis
modular, flexible, and fast.
"""


from proteomics import models
from proteomics import config
from sqlalchemy import (MetaData, Table, Column, Integer, String, ForeignKey,
                       DateTime)
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

tables['proteins'] = Table(
    'proteins', metadata,
    Column('id', String, primary_key=True),
    Column('sequence', String),
    Column('created', DateTime, server_default=text('current_timestamp')),
    Column('modified', DateTime, server_default=text('current_timestamp'),
           server_onupdate=text('current_timestamp')),
)

tables['peptides'] = Table(
    'peptides', metadata,
    Column('id', String, primary_key=True),
    Column('sequence', String),
    Column('created', DateTime, server_default=text('current_timestamp')),
    Column('modified', DateTime, server_default=text('current_timestamp'),
           server_onupdate=text('current_timestamp')),
)

tables['genomes'] = Table(
    'genomes', metadata,
    Column('id', String, primary_key=True),
    Column('created', DateTime, server_default=text('current_timestamp')),
    Column('modified', DateTime, server_default=text('current_timestamp'),
           server_onupdate=text('current_timestamp')),
)

tables['digests'] = Table(
    'digests', metadata,
    Column('id', String, primary_key=True),
    Column('created', DateTime, server_default=text('current_timestamp')),
    Column('modified', DateTime, server_default=text('current_timestamp'),
           server_onupdate=text('current_timestamp')),
)

tables['protein_instances'] = Table(
    'protein_instances', metadata,
    Column('id', Integer, primary_key=True),
    Column('protein_sequence', String, ForeignKey('proteins.sequence')),
    Column('genome_id', String, ForeignKey('genomes.id')),
    Column('metadata', String),
    Column('created', DateTime, server_default=text('current_timestamp')),
    Column('modified', DateTime, server_default=text('current_timestamp'),
           server_onupdate=text('current_timestamp')),
)

tables['peptide_instances'] = Table(
    'digest_products', metadata,
    Column('id', Integer, primary_key=True),
    Column('protein_sequence', String, ForeignKey('proteins.sequence')),
    Column('digest_id', String, ForeignKey('digests.id')),
    Column('peptide_sequence', String, ForeignKey('peptides.sequence')),
    Column('created', DateTime, server_default=text('current_timestamp')),
    Column('modified', DateTime, server_default=text('current_timestamp'),
           server_onupdate=text('current_timestamp')),
)


# Map tables to domain models.
mapper(models.Protein, tables['proteins'])

mapper(models.Peptide, tables['peptides'])

mapper(models.Genome, tables['genomes'])

mapper(models.Digest, tables['digests'])

mapper(models.ProteinInstance, tables['protein_instances'], properties={
    'protein': relationship(models.Protein),
    'genome': relationship(models.Genome)
})

mapper(models.PeptideInstance, tables['peptide_instances'], properties={
    'protein': relationship(models.Protein),
    'digest': relationship(models.Digest),
    'peptide': relationship(models.Peptide)
})

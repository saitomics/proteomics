"""
Proteomics DB.
The goal of the db schema is to make proteomics data ingesta and analysis
modular, flexible, and fast.
"""


from proteomics import models
from proteomics import config
from sqlalchemy import (MetaData, Table, Column, Integer, String, ForeignKey)
from sqlalchemy.orm import mapper, relationship
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
session = scoped_session(sessionmaker(bind=engine))

def get_session():
    return session()

def init_db():
    metadata.create_all(bind=engine, checkfirst=True)

def clear_db():
    metadata.drop_all(bind=engine)

def get_session_w_external_trans(orig_session):
    con = orig_session.bind.connect()
    trans = con.begin()
    new_session = sessionmaker()(bind=con)
    return con, trans, new_session

# Define tables.
metadata = MetaData()

tables = {}

tables['proteins'] = Table(
    'proteins', metadata,
    Column('sequence', String, primary_key=True)
)

tables['peptides'] = Table(
    'peptides', metadata,
    Column('sequence', String, primary_key=True)
)

tables['genomes'] = Table(
    'genomes', metadata,
    Column('id', String, primary_key=True)
)

tables['digests'] = Table(
    'digests', metadata,
    Column('id', String, primary_key=True)
)

tables['digest_products'] = Table(
    'digest_products', metadata,
    Column('protein_sequence', String, 
           ForeignKey('proteins.sequence'), primary_key=True),
    Column('digest_id', String,
           ForeignKey('digests.id'), primary_key=True),
    Column('peptide_sequence', String, 
           ForeignKey('peptides.sequence'), primary_key=True),
)

tables['protein_instances'] = Table(
    'protein_instances', metadata,
    Column('id', Integer, primary_key=True),
    Column('protein_sequence', String, 
           ForeignKey('proteins.sequence')),
    Column('genome_id', String, 
           ForeignKey('genomes.id')),
    Column('metadata', String),
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

mapper(models.DigestProduct, tables['digest_products'], properties={
    'protein': relationship(models.Protein),
    'digest': relationship(models.Genome),
    'peptide': relationship(models.Peptide)
})

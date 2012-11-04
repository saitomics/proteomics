"""
Proteomics Schema.
The goal of this schema is to make proteomics data ingesta and analysis
modular and flexible.
"""

from sqlalchemy import (MetaData, Table, Column, Integer, String, ForeignKey)


# Initialize Metadata.
metadata = MetaData()

# Define tables.
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

"""
We represent the results of a digest as 
protein-digest-peptide triples.
"""
tables['digest_products'] = Table(
    'digest_products', metadata,
    Column('protein_sequence', String, 
           ForeignKey('proteins.sequence'), primary_key=True),
    Column('digest_id', String,
           ForeignKey('digests.id'), primary_key=True),
    Column('peptide_sequence', String, 
           ForeignKey('peptides.sequence'), primary_key=True),
)

"""
A protein instance is a single occurence of a protein
that occurs within a dataset. Typically this dataset
is a genome.
We use protein records because the same protein can appear multiple
times w/in a genome.
"""
tables['protein_instances'] = Table(
    'protein_instances', metadata,
    Column('id', Integer, primary_key=True),
    Column('protein_sequence', String, 
           ForeignKey('proteins.sequence')),
    Column('genome_id', String, 
           ForeignKey('genomes.id')),
    # Hang on to metadata about the instance.
    # We may use this later to reconcile proteins
    # with external databases.
    Column('metadata', String),
)

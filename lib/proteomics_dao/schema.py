"""
Proteomics Schema.
The goal of this schema is to make proteomics data ingesta and analysis
modular and flexible.
"""

# Define tables.
tables = {}

tables['proteins'] = Table(
    'proteins', metadata,
    Column('id', String, primary_key=True),
    Column('sequence', String)
)

tables['peptides'] = Table(
    'peptides', metadata,
    Column('id', String, primary_key=True),
    Column('sequence', String)
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
Here comes the Greek...
A 'Proteolysis' is the breakdown of a protein into sub-entities.
These sub-entities are typically peptides.
We represent a proteolysis record as a
protein-digest pair.
"""
tables['proteolyses'] = Table(
    'proteolyses', metadata,
    Column('protein_id', String, 
           ForeignKey('proteins.id'), primary_key=True),
    Column('digest_id', String, 
           ForeignKey('digests.id'), primary_key=True),
)

"""
A proteolysis_product represents a sub-entity produced by
a proteolysis. This is typically a peptide.
"""
tables['proteolysis_products'] = Table(
    # Composite foreign-key for proteolyses.
    Column('protein_id', String, nullable=False, primary_key=True),
    Column('digest_id', String, nullable=False, primary_key=True),
    ForeignKeyConstraint(
        ['protein_id', 'digest_id'], 
        ['proteolyses.protein_id', 'proteolyses.digest_id']
    ),
    Column('peptide_id', String, 
           ForeignKey('peptides.id'), primary_key=True),
)

"""
A protein instance is a single occurence of a protein
that occurs within a dataset. Typically this dataset
is a genome.
We use protein records because the same protein can appear multiple
times w/in a genome.
"""
#@TODO change this to genomes_proteins?
tables['protein_instances'] = None

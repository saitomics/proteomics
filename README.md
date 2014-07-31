Saito Lab: Computational Proteomics Tools
==============

This repository contains a set of computational tools for analyzing proteomics data.

## General System Description

These tools are intended to help researchers answer questions about proteomics data. 

Some specific questions that these tools help provide answers for include:

- Is tryptic peptide XXX found in Proteome A and Proteome B?
- How many tryptic peptides do Proteome A and Proteome B have in common?
- Are tryptic peptides XXX and YYY both found in Proteome A?
- How many tryptic peptides are there in Proteome A that differ from peptide XXX by n positions?

The analysis tools consist of:

1): a database, stored in a standalone SQLite file.  
2): python libraries, for processing, ingesting, and analyzing data 
3): command-line scripts, to act as interfaces to the python libraries and the database.

Please note that this is *not* designed as a high-performance/high-volume solution; Instead it is intended to function as a quick-and-easy testing bed for doing computational analyses of proteomics data.

## Installation

These instructions assume that you are running within a unix environment that has python2.7 .

1. **Install virtualenv**: http://www.virtualenv.org/en/latest/virtualenv.html#installation
2. **Create a virtualenv**: From the directory that contains this README.md file, run this command: ````virtualenv py2.7```` . This will create a new python virtual environment in the directory 'py2.7'.
3. **Install dependencies via pip**: Still in the same directory, run this command: ````bin/install_requirements.sh````. This will install other python libraries that are necessary for these tools to work. (currently, just the SqlAlchemy library).
4. **Run the tests**: Check that everything works by running this commmand: ````bin/run_tests.sh```` . You should see a bunch of output, with the last line reading 'OK'.
5. **Initialize the Database**: Run this command: ````bin/initialize_db.sh```` . This will create a database file named 'proteomics.db.sqlite'.
6 (optional). **Install the sqlite3 command-line client**: If you wish run your own SQL queries on the protein db, it is recommended that you install the sqlite3 client. This should be possible through your system's package manager. E.g. on Ubuntu, the command to do this would look like ````sudo apt-get install sqlite3````.

## Quick Usage Guide

### 1: Digest and ingest data
1. Run the script bin/digest_and_ingest.sh with FASTA proteome files you wish to digest and ingest. e.g.:
````
bin/digest_and_ingest.sh file1.fasta file2.fasta ...
````

This script reads the FASTA files, and runs digestions on their sequences. You should see a fair amount of output as these files are processed.

### 2: Generate redundancy tables
1.: See available taxon ids by querying DB: e.g. 
````
bin/list_taxon_ids.sh
````
2.: Generate redundancy tables for groups of taxons e.g.
````
bin/generate_redundancy_tables.sh --taxon-ids syn8102 syn7502 syn7503 --output-dir exampleRedundancyTables
````

3.: View resulting files in exampleRedundancyTables
    - counts.csv contains counts of redundant peptides
    - percents.csv contains the values in counts.csv, divided by the number of unique peptides in the *union* of digestions of a taxa pair.

### 3. Run your own SQL Query
If you installed the sqlite3 command-line client, as per step #6 in the installation instructions, you can use it to run your own SQL queries. e.q.
````
sqlite3 redundancy.db.sqlite "SELECT taxon.id FROM taxon"
````

Some example SQL queries are provided further down in this README.

### 4.  Query sequences for taxon matches:
You can query the database for exact and fuzzy matches. e.g.:
````
bin/query_by_sequence.sh --sequence MGFPCNR --max-distance 1
````

### 5.(optional, expected to occur rarely): Clear data for a given set of taxa.
If you wish to **delete** data for a given set of taxa in the db, run a command like this:
````
bin/clear_taxon_data.sh --taxon-ids croc5801
````


## Using the Database
The redundancy database is a SQLite standalone database file. 

It can be accessed the SQLite command line client e.g.
sqlite3 redundancy.db.sqlite

Use of the sqlite3 client is out of the scope of this document. Run the command
'man sqlite3' for more information about the sqlite3 client. 
(type 'q' to leave the man page)

For general SQL tutorials, try this site: http://sqlzoo.net/

If you plan to use the database, it is recommended that you understand the
'Database Schema' section below. You may also find the 'Example Queries' section
to be useful.

## Database Schema
This section describes the redundancy database tables and their relationships
(the schema).

The goals of the schema are:
- to make analysis fast
- to make queries simple
- to provide flexibility to answer wide range of questions

### Tables

#### taxon
description: taxon proteome record
columns:
- id

#### protein
description: canonical protein records
columns:
- id
- sequence (notated as amino acid residues)
- mass

#### taxon_protein
description: records if taxon proteome X contains protein Y
columns:
- id
- taxon_id (foreign key to taxon.id)
- protein_id (foreign key to protein.id)
- metadata (metadata associated with the occurence of the protein, 
            e.g. FASTA headers or NIH IDs)

#### peptide
description: canonical peptide records
columns:
- id
- sequence (in amino acid residues)
- mass

#### protease
description: protease records
columns: 
- id
- cleavage_rule (rule for how this protease cleaves an amino acid sequence.
  Normally this is a regular expression)

#### digest
description: digest records
columns:
- id
- protease_id (foreign key to protease.id)
- max_missed_cleavages
- min_acids (ignore any peptides with < this many acids)
- max_acids (ignore any peptides with > this many acids)

#### taxon_digest
description: records whether taxon proteome X has been digested with digest Y
columns:
- id
- taxon_id (foreign key to taxon.id)
- digest_id (foreign key to digest.id)

#### protein_digest
description: records whether protein X has been digested with digest Y
columns:
- id
- protein_id (foreign key to protein.id)
- digest_id (foreign key to digest.id)

#### protein_digest_peptide
description: records if petide X is a product of protein_digest Y
columns:
- id
- peptide_id (foreign key to peptide.id)
- protein_digest_id (foreign key to protein_digest.id) 
- count (# of times peptide X appeared in protein_digest Y)

#### protein_digest_peptide
description: records if petide X is a product of taxon_digest Y
columns:
- id
- peptide_id (foreign key to peptide.id)
- taxon_digest_id (foreign key to taxon_digest.id) 
- count (# of times peptide X appeared in taxon_digest Y)

### Example Queries

#### Count unique peptides in a taxon digest
````
SELECT
 count(*)
FROM
 taxon_digest_peptide
 JOIN taxon_digest ON taxon_digest_peptide.taxon_digest_id = taxon_digest.id
 JOIN taxon ON taxon_digest.taxon_id = taxon.id
 JOIN digest on taxon_digest.digest_id = digest.id
WHERE
 taxon.id = 'syn7805'
 AND digest.id = 1
````
 
#### Count number of proteins that occur multiple times in a taxon proteome
````
SELECT 
 COUNT(*) AS multiply_occuring_proteins
FROM (
 SELECT 
  COUNT(protein.id) AS num_instances
 FROM
  taxon_protein
  JOIN taxon ON taxon_protein.taxon_id = taxon.id
  JOIN protein ON taxon_protein.protein_id = protein.id
 WHERE
  taxon.id = 'syn7805'
 GROUP BY
  protein.id
 HAVING
  num_instances > 1
) AS subquery
````

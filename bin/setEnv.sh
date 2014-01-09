#!/bin/bash


# Get the proteomics base dir.
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.."

# Activate virtualenv
source $BASE_DIR/py2.7/bin/activate

# Set python path to include proteomics
export PYTHONPATH="$PYTHONPATH:$BASE_DIR/lib"

# Set path to database
export PROTEOMICS_DB="$BASE_DIR/proteomics.db.sqlite"

# Set path to SQLLite Levenshtein extension.
export SQLITE_LEVENSTHEIN="$BASE_DIR/lib/levenshtein.sqlext"


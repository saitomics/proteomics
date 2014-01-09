#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Set environment variables.
. $DIR/setEnv.sh

# Initialize the db.
python -c "import proteomics.db as db; db.init_db()"

echo "Initialized DB at '$PROTEOMICS_DB'"

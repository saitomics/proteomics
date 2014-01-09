#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

. $DIR/setEnv.sh

sqlite3 $PROTEOMICS_DB "SELECT * FROM taxon;"


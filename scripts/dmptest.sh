#!/bin/bash

# THISPID=$$
SCRIPT_PATH="${BASH_SOURCE[0]}"
cd "`dirname "${SCRIPT_PATH}"`"

sleep 10
python updateRunStatus.py -s '1' -f $1

python saveReadsNumber.py -i 'scripts/readsnumber.tsv'

sleep 10
python updateRunStatus.py -s '2' -f $1

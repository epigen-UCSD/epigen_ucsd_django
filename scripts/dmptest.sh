#!/bin/bash

THISPID=$$
SCRIPT_PATH="${BASH_SOURCE[0]}"
cd "`dirname "${SCRIPT_PATH}"`"

sleep 10
python updateRun.py -s '1' -j $THISPID

sleep 10
python updateRun.py -s '2' -j $THISPID

#!/bin/bash

# THISPID=$$
SCRIPT_PATH="${BASH_SOURCE[0]}"
cd "`dirname "${SCRIPT_PATH}"`"

sleep 5
python updateLibrariesSetQC.py -s '1' -id $1

python updateLibrariesSetQC.py \
-url 'http://epigenomics.sdsc.edu:8088/Set_70_test/69ec5ea434b42b06f29bebc97d063ca7//setQC_report_chip_test.html' \
-v 'e3673a1' -id $1

##################################################
## Step 1. Check 
python updateLibrariesSetQC.py -s '2' -id $1

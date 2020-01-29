#!/bin/bash

# THISPID=$$
SCRIPT_PATH="${BASH_SOURCE[0]}"
cd "`dirname "${SCRIPT_PATH}"`"

python encode_step2_rt_rl_correction_and_fq_transfering.py -f $1

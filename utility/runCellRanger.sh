#!/bin/bash

#Description: This script is used to handle a 10x `cellranger count` job submission

SEQ=$1
REF_GEN_LOCATION=$2
TENX_DIR=$3
USER_EMAIL=$4

TENXFILE=${TENX_DIR}${SEQ}"/."${SEQ}".tsv"
TYPE2='10xCellRangerRNA' 
#only one job shuold be submitted with this
n_libs=$( wc -l $TENXFILE |  awk '{print $1}'  )
cmd1="qsub -k oe -t 0-$[n_libs-1] -v samples=${TENXFILE},genome_path=${REF_GEN_LOCATION} -M $USER_EMAIL -q hotel -l walltime=24:00:00 \$(which run10xCellRanger.pbs)"
echo "${cmd1}"
job1=$(ssh zhc268@tscc-login.sdsc.edu $cmd1)

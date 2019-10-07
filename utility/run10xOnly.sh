#!/bin/bash

SEQ=$1
TENX_DIR=$2
USER_EMAIL=$3

TENXFILE=${TENX_DIR}${SEQ}"/."${SEQ}"_samplesheet.tsv"
TYPE2='10xATAC'
n_libs=$( awk '{print $1}'  $TENXFILE | wc -l )
awk '{print $1}'  $TENXFILE|while read l; do mkdir -p /projects/ps-epigen/outputs/10xATAC/$l; touch /projects/ps-epigen/outputs/10xATAC/${l}/.inqueue;done
cmd1="qsub -t 0-$[n_libs-1] -v samples=${TENXFILE} -M $USER_EMAIL -q hotel -l walltime=24:00:00 \$(which run10xPipeline.pbs)"
echo "${cmd1}"
job1=$(ssh brg029@tscc-login.sdsc.edu $cmd1)
    
    #touch .inqueue for each lib here
    
    #TODO feedback that job was submitted for 10x
awk '{print $1}' $TENXFILE | while read l; do touch /projects/ps-epigen/outputs/10xATAC/${l}/.inqueue;done 
#!/bin/bash

EMAIL=$1
SEQ=$2
#PARAMSTRING=$(printf "%q\n" "$3")
PARAMSTRING=$3
echo $PARAMSTRING

cmd2="qsub -k oe -M $EMAIL -v OUTPUTNAME=${SEQ},INPUTNAME=${SEQ},DATASETNAME=${SEQ},${PARAMSTRING%,} /projects/ps-epigen/software/snATACCoolAdmin_LIMS/10x_model.bash"
echo $cmd2

job1=$(ssh zhc268@tscc-login.sdsc.edu ${cmd2})


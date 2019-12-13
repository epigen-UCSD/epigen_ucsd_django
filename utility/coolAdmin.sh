#!/bin/bash

EMAIL=$1
SEQ=$2
PIPELINE=$3
PARAMSTRING=$4
cmd1="conda activate /home/opoirion/prog/conda_env/"
echo $cmd1
cmd2="qsub -v OUTPUTNAME=${SEQ},INPUTNAME=${SEQ},DATASETNAME=${SEQ},${PARAMSTRING} /home/opoirion/data/ps-epigen_job/LIMS/10x_model.bash"
echo $cmd2

job1=$(ssh zhc268@tscc-login.sdsc.edu ${cmd1}; ${cmd2})


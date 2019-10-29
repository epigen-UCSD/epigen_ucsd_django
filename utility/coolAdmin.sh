#!/bin/bash

EMAIL=$1
SEQ=$2cmd
PIPELINE=$3
SPECIES=$4
cmd1="conda activate /home/opoirion/prog/conda_env/"
cmd2="qsub -V VERSION=${PIPELINE},GENOMETYPE=${SPECIES},OUTPUTNAME=${SEQ},INPUTNAME=${SEQ},DATASETNAME=${SEQ}  /home/opoirion/data/ps-epigen_job/LIMS/10x_model.bash"
job1=$(ssh brg029@tscc-login.sdsc.edu ${cmd1}; $cmd2)


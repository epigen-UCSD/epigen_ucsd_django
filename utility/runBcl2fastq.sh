#!/bin/bash

## cmd1: qsub bcl2fastq job
flowcell=$1; rundir=$2; useremail=$3
cmd1="qsub -M $useremail -v flowcell_id=$flowcell,run_dir=$rundir \$(which runBcl2fastq.pbs)"
ssh zhc268@tscc-login.sdsc.edu $cmd1


## cmd2: 



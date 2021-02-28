#!/bin/bash

## cmd1: qsub job from tscc 
flowcell=$1; rundir=$2; useremail=$3; tsccaccount=$4;
cmd1="qsub -k oe  -M $useremail -v flowcell_id=$flowcell,run_dir=$rundir \$(which runDemux10xRNA.pbs)"

echo $cmd1
ssh $tsccaccount $cmd1



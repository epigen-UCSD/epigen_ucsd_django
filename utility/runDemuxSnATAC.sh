#!/bin/bash

## cmd1: qsub job from tscc 
flowcell=$1; rundir=$2; useremail=$3
cmd1="qsub -k oe  -M $useremail -v flowcell_id=$flowcell,run_dir=$rundir \$(which runDemuxSnATAC.pbs)"
ssh zhc268@tscc-login.sdsc.edu $cmd1


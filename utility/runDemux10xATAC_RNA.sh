#!/bin/bash

## cmd1: qsub job from tscc 
flowcell=$1; rundir=$2; useremail=$3; extraPars=${@:4:5};
if [ -z $extraPars ]
then
    cmd1="qsub -k oe  -M $useremail -v flowcell_id=$flowcell,run_dir=$rundir \$(which runDemux10xATAC_RNA.pbs)"
else
    cmd1="qsub -k oe  -M $useremail -v flowcell_id=$flowcell,run_dir=$rundir,extraPars=\"$extraPars\" \$(which runDemux10xATAC_RNA.pbs)"
fi

echo $cmd1
ssh zhc268@tscc-login.sdsc.edu $cmd1



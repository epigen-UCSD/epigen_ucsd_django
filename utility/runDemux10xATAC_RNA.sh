#!/bin/bash

## parameters
flowcell=$1; rundir=$2; useremail=$3; extraPars=${@:4:5};

## expand 10x barcode
cd $out_dir
samplesheet=$(find ${rundir}/ -name "SampleSheet.csv" )
barcodefile=/home/zhc268/epigen_ucsd_django/data/nextseq_app/barcodes/chromium-shared-sample-indexes-plate.csv
convertTASampleSheet.py -b $barcodefile -s ${samplesheet}|grep -v "SI-NA"> ${samplesheet/.csv/_rna_expand.csv}

## cmd1: qsub job from tscc 
if [ -z $extraPars ]
then
    cmd1="qsub -k oe  -M $useremail -v flowcell_id=$flowcell,run_dir=$rundir \$(which runDemux10xATAC_RNA.pbs)"
else
    cmd1="qsub -k oe  -M $useremail -v flowcell_id=$flowcell,run_dir=$rundir,extraPars=\"$extraPars\" \$(which runDemux10xATAC_RNA.pbs)"
fi

echo $cmd1
ssh zhc268@tscc-login.sdsc.edu $cmd1



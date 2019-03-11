#!/bin/bash
flowcell=$1; rundir=$2; useremail=$3
## expand 10x barcode
samplesheets=($(find $rundir -name "SampleSheet.csv" ))
barcodefile=/home/zhc268/epigen_ucsd_django/data/nextseq_app/barcodes/chromium-shared-sample-indexes-plate.csv
for s in ${samplesheets[@]}
do
    convertTASampleSheet.py -b $barcodefile -s $s > ${s/SampleSheet.csv/SampleSheet_expand.csv}
done


## cmd1: qsub bcl2fastq job
cmd1="qsub -k oe -M $useremail -v flowcell_id=$flowcell,run_dir=$rundir \$(which runBcl2fastq.pbs)"
ssh zhc268@tscc-login.sdsc.edu $cmd1


## cmd2: 



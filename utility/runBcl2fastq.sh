#!/bin/bash
flowcell=$1; rundir=$2; useremail=$3;exptype=$4;

## expand 10x barcode
samplesheets=($(find ${rundir}/ -name "SampleSheet.csv" ))
barcodefile=/home/zhc268/epigen_ucsd_django/data/nextseq_app/barcodes/chromium-shared-sample-indexes-plate.csv
for s in ${samplesheets[@]}
do
    convertTASampleSheet.py -b $barcodefile -s $s > ${s/SampleSheet.csv/SampleSheet_expand.csv}
done


## cmd1: qsub bcl2fastq job
cmd1="qsub -k oe -M $useremail -v flowcell_id=$flowcell,run_dir=$rundir \$(which runBcl2fastq.pbs)"
job1=$(ssh zhc268@tscc-login.sdsc.edu $cmd1)

## cmd2: qsub 10x demutliplex
#if [ $exptype = 'BT' ]
#then
#    s=${samplesheets[0]};ss=${s/Sheet/Sheet_I1}
#    echo "Lane,Sample,Index" >$ss
#    grep SI-NA $s | awk -v FS=',' -v OFS=',' '{print "*,"$1,$5}' >>$ss 
#    cmd2="qsub -k oe  -W depend=afterok:$job1 -M $useremail  -v flowcell_id=$flowcell,run_dir=$rundir \$(which runDemux10xATAC.pbs)"
#    ssh zhc268@tscc-login.sdsc.edu $cmd2
#fi




#!/bin/bash

# THISPID=$$
SCRIPT_PATH="${BASH_SOURCE[0]}"
cd "`dirname "${SCRIPT_PATH}"`"
SET_ID=$1
USER_EMAIL=$2
SETQC_DIR="/projects/ps-epigen/outputs/setQCs/"
STATUS_FILE=${SETQC_DIR}"."${SET_ID}.txt
SETQC_FILE=${SETQC_DIR}${SET_ID}.txt
LOG_DIR="/projects/ps-epigen/logs/app/"
RUN_LOG_PIP=${LOG_DIR}$(date +%Y%m%d)"_"${SET_ID}".txt"
TYPE="atac"

##################################################
## Step 1. construct set_xxx.txt
##################################################
awk '(NR>1){print $1}' $STATUS_FILE > $SETQC_FILE

##################################################
## Step 2. process unprocessed libs
##################################################
awk -v FS='\t' '(NR>1&&$4=="No"){print $1,$2}' $STATUS_FILE > $RUN_LOG_PIP
n_libs=$(wc -l $RUN_LOG_PIP | awk '{print $1}')
if [ $n_libs -gt 0 ]
then
    cmd1="qsub -v samples=${RUN_LOG_PIP} -t 0-$[n_libs-1] -M $USER_EMAIL -q home-epigen -l walltime=16:00:00 \$(which runPipeline_fastq.pbs)"
    job1=$(ssh zhc268@tscc-login.sdsc.edu $cmd1)
    python updateLibrariesSetQC.py -s '1' -id $SET_ID # process libs
    cmd2="qsub -W depend=afterokarray:$job1 -M $USER_EMAIL -v set_id=$SET_ID,type=$TYPE  \$(which runSetQC.pbs)"
else
    cmd2="qsub -M $USER_EMAIL -v set_id=$SET_ID,type=$TYPE  \$(which runSetQC.pbs)"
fi

##################################################
##  Step 3. run setQC
##################################################

ssh zhc268@tscc-login.sdsc.edu $cmd2


# update to db (included in runSetQC.pbs)
#cmd="cd /home/zhc268/software/setQC/;git rev-parse --short HEAD"
#ver=$(ssh zhc268@tscc-login.sdsc.edu $cmd)
#url="http://epigenomics.sdsc.edu:8088/${SET_ID}/$(cat ${SETQC_FILE/.txt/.rstr.txt})/setQC_report.html" 
#python updateLibrariesSetQC.py -s '3' -url $url -v $ver -id $SET_ID

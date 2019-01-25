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

## determine how many groups
groups=($(awk '(NR>1){print $2}' $STATUS_FILE|uniq))
n_groups=${#groups[@]}
n_libs=$(awk -v FS='\t' 'BEGIN{n=0};{if(NR>1&&$6=="No") n=n+1}END{print n}' $STATUS_FILE)


## determine which pipeline to run
if [ $n_groups -eq 1 ]
then
    # only one group (assume no input)
    RUN_LOG_PIP=${LOG_DIR}$(date +%Y%m%d)"_"${SET_ID}".txt"
    awk -v FS='\t' '(NR>1&&$6=="No"){print $1,$4,$7}' $STATUS_FILE > $RUN_LOG_PIP
    awk '(NR>1){print $1}' $STATUS_FILE > $SETQC_FILE
    setqc_type="atac_chip"
else
    # more than one groups (assume with input)
    setqc_type="chip"    
fi


## run pipeline and setQC 
if [ $n_libs -gt 0 ]
then
    cmd1="qsub -v samples=${RUN_LOG_PIP},chipseq=true -t 0-$[n_libs-1] -M $USER_EMAIL  \$(which runBulkATAC_fastq.pbs)"
    job1=$(ssh zhc268@tscc-login.sdsc.edu $cmd1)
    python updateLibrariesSetQC.py -s '1' -id $SET_ID # process libs
    cmd2="qsub -W depend=afterokarray:$job1 -M $USER_EMAIL -v set_id=$SET_ID,type=$setqc_type  \$(which runSetQC.pbs)"
else
    cmd2="qsub -M $USER_EMAIL -v set_id=$SET_ID,type=$setqc_type  \$(which runSetQC.pbs)"
fi

##################################################
##  Step 3. run setQC
##################################################

ssh zhc268@tscc-login.sdsc.edu $cmd2


#python updateLibrariesSetQC.py -s '3' -url $url -v $ver -id $SET_ID

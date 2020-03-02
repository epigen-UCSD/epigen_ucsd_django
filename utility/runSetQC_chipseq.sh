#!/bin/bash

# THISPID=$$
SCRIPT_PATH="${BASH_SOURCE[0]}"
cd "`dirname "${SCRIPT_PATH}"`"
SET_ID=$1
USER_EMAIL=$2
SET_NAME=$3


SETQC_DIR="/projects/ps-epigen/outputs/setQCs/"
STATUS_FILE=${SETQC_DIR}"."${SET_ID}.txt
SETQC_FILE=${SETQC_DIR}${SET_ID}.txt
LOG_DIR="/projects/ps-epigen/logs/app/"

## downloading files 
[[ -z $STATUS_FILE ]] && { echo "$STATUS_FILE not found"; exit 1; }
echo "downloading encode files" 
python encode_step2_rt_rl_correction_and_fq_transfering.py -f $STATUS_FILE

## determine how many groups
groups=($(awk '(NR>1){print $2}' $STATUS_FILE|uniq))
n_groups=${#groups[@]}
n_libs=$(awk -v FS='\t' 'BEGIN{n=0};{if(NR>1&&$6=="No") n=n+1}END{print n}' $STATUS_FILE)


## determine which pipeline to run
if [ $(grep -c True $STATUS_FILE) -eq 0 ] 
then
    #  no input
    RUN_LOG_PIP=${LOG_DIR}$(date +%Y%m%d)"_"${SET_ID}.txt
    awk -v FS='\t' '(NR>1&&$6=="No"){print $1,$4,$7}' $STATUS_FILE > $RUN_LOG_PIP
    awk '(NR>1){print $1}' $STATUS_FILE > $SETQC_FILE
    setqc_type="atac_chip"
else
    # more than one groups (assume with input)
    setqc_type="chip"
    job_array=()
    if [[ $n_libs -gt 0 ]]
    then
        for g in ${groups[@]} # for each group 
        do
        ## check if any lib is not processed in this group $g   

        ## if not processed, need find input    

        ## if input is not processed, need process the whole group  

        ## if input is processed, need add input + the libs not process 

        ## if all processed, continue
        
        RUN_LOG_PIP=${LOG_DIR}$(date +%Y%m%d)"_"${SET_ID}"_${g}.txt"
        awk -v FS='\t' -v gr=$g '(NR>1&&$2==gr){print $1,$4,$7,$3}' $STATUS_FILE > $RUN_LOG_PIP
        nrow=$(cat $RUN_LOG_PIP|wc -l )
        cmd1="qsub -v samples=${RUN_LOG_PIP},chipseq=true -t 0-$[nrow-1] -M $USER_EMAIL -q hotel -l walltime=24:00:00  \$(which runBulkCHIP_fastq.pbs)"
        job_array+=($(ssh zhc268@tscc-login.sdsc.edu $cmd1))
        done
    fi
    awk '(NR>1){print $1,$2,$3}' $STATUS_FILE > $SETQC_FILE # id,groupid,input
    
fi


## run pipeline and setQC 
if [[ $n_libs -gt 0 ]] && [[ $setqc_type = "atac_chip" ]] 
then
    cmd1="qsub -k oe  -v samples=${RUN_LOG_PIP},chipseq=true -t 0-$[n_libs-1] -M $USER_EMAIL -q hotel -l walltime=24:00:00  \$(which runBulkATAC_fastq.pbs)"
    job1=$(ssh zhc268@tscc-login.sdsc.edu $cmd1)
    ssh zhc268@tscc-login.sdsc.edu "qalter $job1 -W queue=condo"
    python updateLibrariesSetQC.py -s '1' -id $SET_ID # process libs
    cmd2="qsub -k oe -W depend=afterokarray:$job1 -M $USER_EMAIL -v set_id=$SET_ID,set_name='$SET_NAME',type=$setqc_type -q condo  \$(which runSetQC.pbs)"
elif [[ $n_libs -gt 0 ]] && [[ $setqc_type = "chip" ]]
then
    python updateLibrariesSetQC.py -s '1' -id $SET_ID # process libs
    cmd2="qsub -k oe -W depend=afterok:$(echo  ${job_array[@]} | sed 's/ /:/g')  -M $USER_EMAIL -v set_id=$SET_ID,set_name='$SET_NAME',type=$setqc_type -q condo  \$(which runSetQC.pbs)"
else
    cmd2="qsub -k oe  -M $USER_EMAIL -v set_id=$SET_ID,set_name='$SET_NAME',type=$setqc_type -q condo  \$(which runSetQC.pbs)"
fi

##################################################
##  Step 3. run setQC
##################################################

ssh zhc268@tscc-login.sdsc.edu $cmd2


#python updateLibrariesSetQC.py -s '3' -url $url -v $ver -id $SET_ID

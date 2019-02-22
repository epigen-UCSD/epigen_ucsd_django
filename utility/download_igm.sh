#!/bin/bash

cmd1="qsub -k oe -M $5 -v ftp_addr=$1,user=$2,pass=$3,flowcell_id=$4 \$(which download_igm.pbs)"
echo $cmd1
ssh zhc268@tscc-login.sdsc.edu $cmd1



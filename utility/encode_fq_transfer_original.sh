#!/bin/bash
# usage: ./encode_fq_transfer.sh template_seq_tsv_file seqdata_folder
# e.g: ./encode_fq_transfer.sh sequencings.tsv /projects/ps-epigen/seqdata
seq_info_file=$1
seqfolder=$2
while IFS=$'\t' read -r -a myArray
do
	seqid=${myArray[6]}
	seqtype=${myArray[11]}
	fqurl=${myArray[16]}
	echo $seqid

	if [ "${myArray[11]}" == "SE" ]; then
		IFS="/" read -r -a array <<< "$fqurl"
		r1=${array[@]: -1:1}
		r1rename=$seqfolder"/"$seqid".fastq.gz"
		echo $seqfolder"/ENCODE/"$r1
		echo $r1rename
		wget -nc -P $seqfolder"/ENCODE/" $fqurl
		ln -s $seqfolder"/ENCODE/"$r1 $r1rename
	elif [ "${myArray[11]}" == "PE" ]; then
		IFS=',' read -r -a array <<< "$fqurl"
		IFS="/" read -r -a subarray <<< "${array[0]}"
		r1=${subarray[@]: -1:1}
		r1rename=$seqfolder"/"$seqid"_R1.fastq.gz"
		echo $seqfolder"/ENCODE/"$r1
		echo $r1rename
		wget -nc -P $seqfolder"/ENCODE/" ${array[0]}
		ln -s $seqfolder"/ENCODE/"$r1 $r1rename
		IFS="/" read -r -a subarray <<< "${array[1]}"
		r2=${subarray[@]: -1:1}
		r2rename=$seqfolder"/"$seqid"_R2.fastq.gz"
		echo $seqfolder"/ENCODE/"$r2
		echo $r2rename
		wget -nc -P $seqfolder"/ENCODE/" ${array[1]}
		ln -s $seqfolder"/ENCODE/"$r2 $r2rename
	fi


done < $seq_info_files
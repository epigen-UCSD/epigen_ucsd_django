#!/bin/bash
seq_info_file=$1
seqfolder=$2
echo $seq_info_file
# while read -r line;do
# 	cut -f17 $line
# done < "$seq_info_file"

# for i in `cut -f7,17 $seq_info_file`
# do
# 	echo $i
# 	echo 'hhhhh'
# done
while IFS=$'\t' read -r -a myArray
do
	seqid=${myArray[6]}
	seqtype=${myArray[11]}
	fqurl=${myArray[16]}
	echo "$seqid"
	echo "$seqtype"
	echo "$fqurl"
	if [ "${myArray[11]}" == "SE" ]; then
		IFS="/" read -r -a array <<< "$fqurl"
		r1=${array[@]: -1:1}
		echo $seqfolder"/ENCODE/"$r1
		echo $seqfolder"/"$seqid".fastq.gz"
	elif [ "${myArray[11]}" == "PE" ]; then
		IFS=',' read -r -a array <<< "$fqurl"
		IFS="/" read -r -a subarray <<< "${array[0]}"
		r1=${subarray[@]: -1:1}
		echo $seqfolder"/ENCODE/"$r1
		echo $seqfolder"/"$seqid".fastq.gz"
		IFS="/" read -r -a subarray <<< "${array[1]}"
		r2=${subarray[@]: -1:1}
		echo $seqfolder"/ENCODE/"$r2
		echo $seqfolder"/"$seqid".fastq.gz"
	fi


done < $seq_info_file
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
	wget -P $seqfolder"/ENCODE/" $fqurl

done < $seq_info_file
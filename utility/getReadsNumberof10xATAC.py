#!/usr/bin/env python
import os
import sys
import argparse
import subprocess
import json

def main():
	# python getReadsNumberof10xATAC.py -f '/projects/ps-epigen/nextSeq/190116_NB501692_0097_AHJMJNBGX9'
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='Nextseqdir')
    this_dir = parser.parse_args().f
    fastq_dir = os.path.join(this_dir,"Data/Fastqs/")
    read_cnt_tsv = os.path.join(this_dir,"Data/Fastqs/reads_cnt.tsv")
    #log_files=subprocess.check_output("find "+fastq_dir+" -name DemultiplexingStats.xml",shell=True,universal_newlines=True).split()
    #print(log_files)
    json_file = subprocess.check_output("find "+fastq_dir+" -name Stats.json",shell=True,universal_newlines=True).split()
    #print(json_file)
    lib_counts = {}
    lib_counts["Undetermined"] = 0
    with open(json_file[0]) as f:
    	data = json.load(f)
    	for l in data["ConversionResults"]:
    		for s in l["DemuxResults"]:
    			#print(s["SampleName"])
    			#print(s["NumberReads"])
    			if s["SampleName"] not in lib_counts.keys():
    				lib_counts[s["SampleName"]] = s["NumberReads"]
    			else:
    				lib_counts[s["SampleName"]] += s["NumberReads"]
    		lib_counts["Undetermined"] += l["Undetermined"]["NumberReads"]
    #print(lib_counts)
    with open(read_cnt_tsv,'w') as fw:
    	for k,v in lib_counts.items():
    		fw.write('\t'.join([k,str(v)]))
    		fw.write('\n')


if __name__ == '__main__':
    main()

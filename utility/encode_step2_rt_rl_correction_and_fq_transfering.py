#!/usr/bin/env python
import os
import sys
import argparse
import django
from django.conf import settings
import requests
import json
import subprocess

os.chdir("../")
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()
from masterseq_app.models import SeqInfo,LibraryInfo

def main():
    # python encode_step2_rt_rl_correction_and_fq_transfering.py -f .Set_198.txt
    parser = argparse.ArgumentParser()
    parser.add_argument('-f',help = 'the .Set_###.txt file')
    setqcoutdir = settings.SETQC_DIR
    encodetmdir = settings.ENCODE_TM_DIR
    fqdir = settings.FASTQ_DIR

    status_file = os.path.join(setqcoutdir,parser.parse_args().f)
    headers = {'accept': 'application/json'}
    with open(status_file, 'r') as f:
        next(f)
        for line in f:
            fields = line.strip('\n').split('\t')
            if fields[5] == 'No' and fields[0].startswith('ENCODE_'):
                seq_info = SeqInfo.objects.get(seq_id=fields[0])
                lib_info = seq_info.libraryinfo
                lib_accession = lib_info.notes.split(';')[1].split(':')[1]
                uuid = seq_info.notes.split(';')[0].split(':')[1]
                this_url = "https://www.encodeproject.org/replicates/"+uuid+"/?frame=embedded"
                print(this_url)
                response = requests.get(this_url, headers=headers)
                this_seq = response.json()
                for file in this_seq['experiment']['files']:
                    this_file_url = "https://www.encodeproject.org/"+file+"/?frame=embedded"
                    response = requests.get(this_file_url, headers=headers)
                    this_file = response.json()
                    if this_file['file_format']=="fastq":
                        if this_file['replicate']['uuid']==uuid:
                            read_type = this_file['run_type']
                            read_length = this_file['read_length']
                            print(read_length)
                            print(read_type)                                                   
                            if read_type == 'single-ended':
                                accession_number = this_file['accession']
                                fq_url = "https://www.encodeproject.org"+this_file['href']
                                print(lib_accession+'::::'+accession_number+'::::'+fq_url)                               
                                cmd_wget = "wget -nc -P "+ encodetmdir + "/ "+fq_url
                                print(cmd_wget)
                                subprocess.call(cmd_wget,shell=True)
                                r1_origin = os.path.join(encodetmdir,fq_url.rsplit('/',1)[1])                           
                                r1_newname = os.path.join(fqdir,fields[0]+'.fastq.gz')
                                cmd_ln = 'ln -s '+ r1_origin +' ' + r1_newname
                                print(cmd_ln)
                                subprocess.call(cmd_ln,shell=True)

            
    print(status_file)


if __name__ == '__main__':
    main()


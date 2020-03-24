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
    # python encode_step2_rt_rl_correction_and_fq_transfering.py -f .Set_199.txt
    # first check whether this set contains not processed ENCODE_ data, if there is, then download fastq file, retrieve read type and read length, then stored to LIMS metadata, at last rewrite the .Set_###.txt file
    parser = argparse.ArgumentParser()
    parser.add_argument('-f',help = 'the .Set_###.txt file')
    setqcoutdir = settings.SETQC_DIR
    encodetmdir = settings.ENCODE_TM_DIR
    fqdir = settings.FASTQ_DIR

    status_file = os.path.join(setqcoutdir,parser.parse_args().f)
    headers = {'accept': 'application/json'}
    writelines = []

    with open(status_file, 'r') as f:

        fields = next(f).strip('\n').split('\t')
        writelines.append('\t'.join(fields))
        process_index = fields.index('Processed Or Not')
        readtype_index = fields.index('Read Type')
        for line in f:
            fields = line.strip('\n').split('\t')
            
            if fields[process_index] == 'No' and fields[0].startswith('ENCODE_'):
                fq_accession = ''
                seq_info = SeqInfo.objects.get(seq_id=fields[0])                
                uuid = seq_info.notes.split(';')[0].split(':')[1]
                this_url = "https://www.encodeproject.org/replicates/"+uuid+"/?frame=embedded"
                print(fields[0])
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
                            if read_type == 'single-ended':
                                accession_number = this_file['accession']
                                fq_accession = ','.join([fq_accession,accession_number]).strip(',')
                                fq_url = "https://www.encodeproject.org"+this_file['href']
                                #print(lib_accession+'::::'+accession_number+'::::'+fq_url)                               
                                cmd_wget = "wget -cq -P "+ encodetmdir + "/ "+fq_url
                                print(cmd_wget)
                                subprocess.call(cmd_wget,shell=True)
                                origin = os.path.join(encodetmdir,fq_url.rsplit('/',1)[1])                           
                                newname = os.path.join(fqdir,fields[0]+'.fastq.gz')
                                cmd_ln = 'ln -fs '+ origin +' ' + newname
                                print(cmd_ln)
                                subprocess.call(cmd_ln,shell=True)

                            elif read_type == 'paired-ended':
                                accession_number = this_file['accession']
                                fq_accession = ','.join([fq_accession,accession_number]).strip(',')
                                r1_or_r2 = this_file['paired_end']
                                fq_url = "https://www.encodeproject.org"+this_file['href']                            
                                cmd_wget = "wget -cq -P "+ encodetmdir + "/ "+fq_url
                                print(cmd_wget)
                                subprocess.call(cmd_wget,shell=True)
                                origin = os.path.join(encodetmdir,fq_url.rsplit('/',1)[1])                           
                                newname = os.path.join(fqdir,fields[0]+'_R'+str(r1_or_r2)+'.fastq.gz')
                                cmd_ln = 'ln -sf '+ origin +' ' + newname
                                print(cmd_ln)
                                subprocess.call(cmd_ln,shell=True)
                seq_info.read_length = str(read_length)
                if read_type == 'single-ended':
                    seq_info.read_type = 'SE'
                elif read_type == 'paired-ended':
                    seq_info.read_type = 'PE'
                if seq_info.notes.find(fq_accession) == -1:
                    notes_new = ';'.join([seq_info.notes,'ENCODE file accession(s) '+fq_accession])
                    seq_info.notes = notes_new
                seq_info.save()
                writelines.append('\t'.join(['\t'.join(fields[0:readtype_index]),seq_info.read_type,'\t'.join(fields[readtype_index+1:len(fields)])]))
            else:
                writelines.append('\t'.join(fields))

    # rewrite .Set_###.txt file with read type available
    with open(status_file, 'w') as fw:
        fw.write('\n'.join(writelines))

            
    print(status_file)


if __name__ == '__main__':
    main()


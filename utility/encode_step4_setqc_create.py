#!/usr/bin/env python
# Time-stamp: <2019-01-23 10:05:21>

import os
import sys
import django
import io
import argparse
from datetime import datetime
from django.contrib.auth.models import User

os.chdir("../")
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()
from masterseq_app.models import SeqInfo
from setqc_app.models import LibrariesSetQC,LibraryInSet



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-se',help = 'seq.tsv from step2')
    parser.add_argument('-n',help = 'Set name')
    parser.add_argument('-e',help = 'experiment type')
    parser.add_argument('-g',help = 'genome')
    parser.add_argument('-notes',help = 'notes of this setqc')
    parser.add_argument('-user',help = 'the user(username) who requests this ENCODE setqc')

    
    seqfile = parser.parse_args().se
    setname = parser.parse_args().n
    setexp = parser.parse_args().e
    setnote = parser.parse_args().notes
    setgenome = parser.parse_args().g
    username_tm = parser.parse_args().user


    print(seqfile)
    labels = {}
    with open(seqfile, 'r') as f:
        for line in f:
            fields = line.strip('\n').split('\t')
            labels[fields[0].strip()] = fields[1].strip()
    set_ids = list(LibrariesSetQC.objects.values_list('set_id', flat=True))
    maxid = max([int(x.split('_')[1]) for x in set_ids])
    setinfo = LibrariesSetQC.objects.create(set_id = '_'.join(['Set', str(maxid+1)]))
    setinfo.set_name = setname
    setinfo.requestor = User.objects.get(username=username_tm)
    setinfo.experiment_type = setexp
    setinfo.notes = setnote
    setinfo.date_requested = datetime.now().strftime("%Y-%m-%d")
    setinfo.save()
    for k in labels.keys():
        if setexp.lower() == 'chip-seq':
            LibraryInSet.objects.create(
                librariesetqc=setinfo,
                seqinfo=SeqInfo.objects.get(seq_id=k),
                is_input=False,
                group_number=1,
                label=labels[k],
                genome=GenomeInfo.objects.get(genome_name=setgenome)
                )
        else:
            LibraryInSet.objects.create(
                librariesetqc=setinfo,
                seqinfo=SeqInfo.objects.get(seq_id=k),
                label=labels[k],
                genome=GenomeInfo.objects.get(genome_name=setgenome)
                ) 
    out_for_processing = '_'.join(['Set', str(maxid+1)+'.txt'
           

if __name__ == '__main__':
    main()

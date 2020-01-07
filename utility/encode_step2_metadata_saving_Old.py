#!/usr/bin/env python
# Time-stamp: <2019-01-23 10:05:21>

import os
import sys
import django
import io
import argparse
from epigen_ucsd_django.shared import datetransform
from django.contrib.auth.models import Group,User

os.chdir("../")
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()
from masterseq_app.models import SampleInfo,LibraryInfo,SeqInfo



def main():


    parser = argparse.ArgumentParser()
    parser.add_argument('-sa',help = 'path for sample.tsv file')
    parser.add_argument('-l',help = 'path for library.tsv file')
    parser.add_argument('-se',help = 'path for sequencing.tsv file')
    parser.add_argument('-user',help = 'the user(username) who requests this ENCODE setqc')
    out_for_fq = 'seq_fq.tsv'
    writelines = []
    username_tm = parser.parse_args().user

    if len(sys.argv) != 5:
        parser.print_help(sys.stderr)
        sys.exit(1)

    samplefile = parser.parse_args().sa
    print(samplefile)
    with open(samplefile, 'r') as f:
        for line in f:
            fields = line.strip('\n').split('\t')
            try:
                samdate = datetransform(fields[0].strip())
            else:
                samdate = None
            gname = fields[1].strip() if fields[1].strip() not in ['NA','N/A'] else ''
            if gname:
                group_tm = Group.objects.get(name=gname)
            else:
                group_tm = None        
            sampleid = fields[8].strip()
            samdescript = fields[9].strip()
            samspecies = fields[10].split('(')[0].lower().strip()
            samtype = fields[11].split('(')[0].strip().lower()
            samnotes = fields[20].strip()
            try:
                SampleInfo.objects.get(sample_id=sampleid)
            else:
                obj = SampleInfo.objects.create(sample_id=sampleid)
                obj.date = samdate
                obj.group = group_tm
                obj.description = samdescript
                obj.species = samspecies
                obj.sample_type = samtype
                obj.notes = samnotes
                obj.team_member = User.objects.get(username=username_tm)
                obj.save()


    libraryfile = parser.parse_args().l
    print(libraryfile)
    lib_new_name = {}
    with open(libraryfile, 'r') as f:
        for line in f:
            fields = line.strip('\n').split('\t')
            sampleid = fields[0].strip()
            lib_des = fields[1].strip()
            username_tm = parser.parse_args().user
            libexp = fields[5].strip()
            libid = fields[8].strip()
            libnote = fields[9].strip()
            thissample = SampleInfo.objects.get(sample_id=sampleid)
            existing_flag = 0
            for item in thissample.libraryinfo_set.all():
                if libid == item.notes.split(';')[0]:
                    obj = item
                    lib_new_name[libid] = item.library_id
                    existing_flag = 1
                    break;
                else:
                    existing_flag = 0
            lib_ids = list(LibraryInfo.objects.values_list('library_id', flat=True))
            maxid = max([int(x.split('_')[1]) for x in lib_ids if x.startswith('ENCODE')])
            libid_new = '_'.join(['ENCODE', str(maxid+1)])
            lib_new_name[libid] = libid_new
            if existing_flag == 0:
                obj = LibraryInfo.objects.create(library_id=libid_new)                  
                obj.sampleinfo = SampleInfo.objects.get(sample_id=sampleid)
                obj.library_description = lib_des
                obj.team_member_initails = User.objects.get(username=username_tm)
                obj.experiment_type = libexp
                obj.notes = ';'.join([libid,libnote])
                obj.save()



    sequencingfile = parser.parse_args().se
    print(sequencingfile)
    with open(sequencingfile, 'r') as f:
        for line in f:
            fields = line.strip('\n').split('\t')
            username_tm = parser.parse_args().user
            seqid = fields[15].strip().split(';')[0].split(')')[1]
            thislibrary =  LibraryInfo.objects.get(library_id=lib_new_name[fields[5].strip()])
            existing_flag = 0
            for item in thislibrary.seqinfo_set.all():
                if seqid == item.notes.split(';')[1].split(')')[1]:
                    obj = item
                    existing_flag = 1
                    writelines.append('\t'.join([item.seq_id,'1',fields[11].strip(),fields[16].strip()]))
                    break;
                else:
                    existing_flag = 0
            if existing_flag == 0:
                counts = thislibrary.seqinfo_set.all().count()
                if counts == 0:
                    thisseqid = lib_new_name[fields[5].strip()]
                else:
                    thisseqid = lib_new_name[fields[5].strip()]+'_'+str(counts+1)
                obj = SeqInfo.objects.create(seq_id=thisseqid)
                obj.libraryinfo = thislibrary
                obj.team_member_initails = User.objects.get(username=username_tm)
                obj.read_length = fields[10].strip()
                obj.read_type = fields[11].strip()
                obj.notes = ';'.join([fields[5].strip()+':'+fields[6.strip(),fields[15].strip()]])
                writelines.append('\t'.join([thisseqid,fields[1].strip(),'0',fields[11].strip(),fields[16].strip()]))
    with open(out_for_fq, 'w') as fw:
        fw.write('\t'.join(['seq_id','label','existed','read_type','download_url']))
        fw.write('\n')
        fw.write('\n'.join(writelines))
        fw.write('\n')

if __name__ == '__main__':
    main()

#!/usr/bin/env python
import os
import sys
import django
import argparse


basedir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(basedir))
sys.path.append(basedir)
sys.path.append(os.path.dirname(basedir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()

from nextseq_app.models import RunInfo, LibrariesInRun


def main():
    '''
    update the runInfo: reads_counts for each lib; status 
    '''

    # for example: python saveReadsNumber.py -f 'xxx|flowcellid'
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='flowcell id')
    parser.add_argument('-i', help='input reads cnt file')
    flowcell = parser.parse_args().f
    readscountfile = parser.parse_args().i

    warning_count_th = 1000
    run_obj = RunInfo.objects.get(Flowcell_ID=flowcell)
    run_obj.jobstatus = 'Done'

    # save reads counts
    with open(readscountfile, 'r') as f:
        for line in f:
            fields = line.strip('\n').split('\t')
            obj = LibrariesInRun.objects.get(Library_ID=fields[0])
            obj.numberofreads = int(fields[1])
            if(obj.numberofreads < warning_count_th):
                run_obj.jobstatus = 'Warning'
            obj.save()

    # save run
    run_obj.save()


if __name__ == '__main__':
    main()

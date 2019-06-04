#!/usr/bin/env python
import os
import sys
import django
import argparse
import subprocess
import xml.etree.ElementTree as ET
# print(os.path.abspath(__file__))


basedir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(basedir))
sys.path.append(basedir)
sys.path.append(os.path.dirname(basedir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()

from nextseq_app.models import RunInfo


def getTotalReads(fq_dir):
    '''
    call shell function to count total reads in the library 
    '''
    log_files = subprocess.check_output(
        "find -L "+fq_dir+" -name DemultiplexingStats.xml", shell=True, universal_newlines=True).split()
    tree = ET.parse(log_files[0])
    flowcell = tree.getroot().getchildren()[0]
    cnts = []
    for p in flowcell.findall('Project'):
        if p.get('name') == 'all':
            for c in p.findall('./Sample/')[0].findall('./Lane/BarcodeCount'):
                cnts.append(int(c.text))
    return(sum(cnts))


def main(flowcell):
    # for example: python updateRunStatus.py -s '0' -f 'H5GLYBGX5fff'
    # if you have dir to save, python updateRunStatus.py -s '0' -d '/Users/180705_AH5GLYBGX5431' -f 'H5GLYBGX5fff'
    obj = RunInfo.objects.get(Flowcell_ID=flowcell)
    this_dir = obj.nextseqdir
    fastq_dir = this_dir  # os.path.join(this_dir, "Data/Fastqs")
    libs = obj.librariesinrun_set.all()
    obj.total_libraries = len(libs)
    total_lib_reads = sum([i['numberofreads'] for i in libs.values()])
    obj.total_reads = getTotalReads(fastq_dir)
    obj.percent_of_reads_demultiplexed = round(
        total_lib_reads/obj.total_reads*100)
    obj.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', help='FlowCellID')
    this_flowcellid = parser.parse_args().f
    main(this_flowcellid)

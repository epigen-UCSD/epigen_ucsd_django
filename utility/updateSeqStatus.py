#!/usr/bin/env python
from datetime import datetime
from django.conf import settings
import os
import sys
import django
import argparse
import subprocess
# print(os.path.abspath(__file__))

basedir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(basedir))
sys.path.append(basedir)
sys.path.append(os.path.dirname(basedir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()


from django.contrib.auth.models import User, Group
from singlecell_app.views import get_seq_status
from singlecell_app.models import SingleCellObject, TenxqcInfo, scRNAqcInfo, CoolAdminSubmission
from masterseq_app.models import SeqInfo, LibraryInfo, SampleInfo

"""
This script is to update seq status in db by scan on the disk 
"""



def check_status(entry):
    #group_id = entry['libraryinfo__sampleinfo__group']
    #group_name = get_group_name(groups, group_id)
    #entry['libraryinfo__sampleinfo__group'] = group_name
    seq_id = entry['seq_id']
    experiment_type = entry['libraryinfo__experiment_type']
    return(get_seq_status(seq_id, entry['read_type'], experiment_type))


def main():
    # get all sc seqs
    seqs_queryset = SeqInfo.objects.all().select_related('libraryinfo', 'libraryinfo__sampleinfo',
                                                         'libraryinfo__sampleinfo__group').values('seq_id', 'libraryinfo__experiment_type', 'read_type')
    print(len(seqs_queryset))  # 1444
    data = list(seqs_queryset)
    print(len(data))
    i = 0
    for entry in data:
        print(i)
        i += 1
        seq_obj = SeqInfo.objects.get(seq_id=entry['seq_id'])
        seq_obj.status = check_status(entry)
        seq_obj.save()


main()

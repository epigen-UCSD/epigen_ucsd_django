#!/usr/bin/env python
import os
from re import sub
import sys
import django
import argparse
# print(os.path.abspath(__file__))


basedir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(basedir))
sys.path.append(basedir)
sys.path.append(os.path.dirname(basedir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()

from masterseq_app.models import SeqInfo
from singlecell_app.views import get_cooladmin_status,get_cooladmin_link
from singlecell_app.models import CoolAdminSubmission

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-id', help='Sequence_ID (e.g. JYH_xxx)')

    seq_id = parser.parse_args().id
    seq_info = SeqInfo.objects.get(seq_id=seq_id)
    submission_obj = CoolAdminSubmission.objects.get(seqinfo=seq_info)
    print(get_cooladmin_status(seq_id,seq_info.id))
    print(get_cooladmin_link(seq_id))
    submission_obj.pipeline_status = get_cooladmin_status(seq_id,seq_info.id)
    submission_obj.link = get_cooladmin_link(seq_id)
    submission_obj.save()

if __name__ == '__main__':
    main()

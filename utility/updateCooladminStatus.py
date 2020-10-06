#!/usr/bin/env python


import os
import sys
import django
import argparse
import subprocess
import json
from django.conf import settings

# setting
basedir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(basedir))
sys.path.append(basedir)
sys.path.append(os.path.dirname(basedir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()


from singlecell_app.views import  get_cooladmin_link,get_cooladmin_status
from datetime import datetime
from singlecell_app.models import SingleCellObject, CoolAdminSubmission
from masterseq_app.models import SeqInfo


# print(os.path.abspath(__file__))

"""
This script should work for both scRNA snRNA and 10xATAC type experiment SingleCellObject models.
"""

# Now this script or any imported module can use any part of Django it needs.

# hold all single cell experiment values
SINGLE_CELL_EXPS = ['10xATAC', 'scRNA-seq', 'snRNA-seq', 'scATAC-seq']

# These should be the only status's passed to the function. #TODO maybe add or force a check?
# No is the same status as ClickToSubmit
status_types = ['Yes', 'No', 'InQueue', 'InProcess', 'Error!', 'ClickToSubmit']




def main(seq_id, status):
    # for example: python updateSingelCellStatus.py -sedid 'MM_130' -tenx_status 'InProcess'
    try:
        seq = SeqInfo.objects.get(seq_id=seq_id)
        seq.save()
        # print(seq.experiment_type)
        sc_obj, _ = SingleCellObject.objects.get_or_create(seqinfo=seq)
        print(sc_obj.experiment_type)
        cool_sub_obj, _ = CoolAdminSubmission.objects.update_or_create(
        seqinfo=seq)
        cool_sub_obj.link = get_cooladmin_link(seq.seq_id)
        cool_sub_obj.submitted= True
        print(cool_sub_obj)
        cool_sub_obj.save()
        print(get_cooladmin_status(seq_id,seq.id))
        cool_sub_obj.pipeline_status = get_cooladmin_status(seq_id,seq.id)
        print(cool_sub_obj.pipeline_status )
        cool_sub_obj.save()
        sc_obj.cooladminsubmission=cool_sub_obj

    except:
        print('not load')
        return

    sc_obj.date_last_modified = datetime.now()
    sc_obj.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-seqid', help='Sequence Seq_id like MM_130')
    parser.add_argument(
        '-status', help='Set 10x pipeline status to such as "InProcess" or "Yes"')
    seq_id = parser.parse_args().seqid
    status = parser.parse_args().status
    main(seq_id, status)

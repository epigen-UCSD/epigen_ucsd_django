#!/usr/bin/env python



import os
import sys
import django
import argparse
import subprocess
from django.conf import settings

# setting
basedir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(basedir))
sys.path.append(basedir)
sys.path.append(os.path.dirname(basedir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()

from singlecell_app.views import get_tenx_status, get_latest_modified_time, insert_link,get_cooladmin_link
from masterseq_app.models import SeqInfo, LibraryInfo, SampleInfo
from singlecell_app.models import SingleCellObject, TenxqcInfo, scRNAqcInfo, CoolAdminSubmission
from django.contrib.auth.models import User
from datetime import datetime
from populate_singlecell_objects import generate_qc_metrics_table

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


def getCooladminStatus(cool_sub_object):
    """
    get cooladminsubmission status by scan the folder COOLADMIN_DIR
    """
    print(cool_sub_object.seqinfo.seq_id)
    
    print(settings.COOLADMIN_DIR)
    return cool_sub_object


def updateCoolAdminStatus(sc_object):
    """
    update or create cooladminsubmission object and linked to sc_object
    """
    cool_sub_obj, _ = CoolAdminSubmission.objects.update_or_create(
        seqinfo=sc_object.seqinfo)

    # scan COOLADMIN_DIR folder to get the status
    #cool_sub_obj = getCooladminStatus(cool_sub_obj)
    cool_sub_obj.link = get_cooladmin_link(sc_object.seqinfo.seq_id)
    cool_sub_obj.save()
    sc_object.cooladminsubmission = cool_sub_obj
    return sc_object


def main(seq_id, status):
    # for example: python updateSingelCellStatus.py -sedid 'MM_130' -tenx_status 'InProcess'
    try:
        seq = SeqInfo.objects.get(seq_id=seq_id)
        seq.save()
        # print(seq.experiment_type)
        sc_obj, _ = SingleCellObject.objects.get_or_create(seqinfo=seq)
        print(sc_obj.experiment_type)
    except:
        return
    sc_obj = updateCoolAdminStatus(sc_obj)
    sc_obj.date_last_modified = datetime.now()
    dir_to_expts = settings.TENX_DIR if sc_obj.experiment_type in [
        "10xATAC", "scATAC-seq"] else settings.SCRNA_DIR
    summary_file = os.path.join(dir_to_expts, seq_id, 'outs/web_summary.html')
    sc_obj.tenx_pipeline_status = status

    if(status == 'Yes' and os.path.exists(summary_file)):

        # make qc metrics table and save it to SCmodel's generic foreign key
        sc_obj.content_object = generate_qc_metrics_table(
            seq_id, sc_obj.experiment_type)

        # update symbolic links
        #print(insert_link(os.path.join(dir_to_expts,seq_id,'outs/web_summary.html'), seq_id, sc_obj.experiment_type))
        sc_obj.random_string_link = insert_link(
            summary_file, seq_id, sc_obj.experiment_type)
    elif(status == 'Yes'):
        # not finished actually
        sc_obj.tenx_pipeline_status = 'ClickToSubmit'

    sc_obj.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-seqid', help='Sequence Seq_id like MM_130')
    parser.add_argument(
        '-tenx_status', help='Set 10x pipeline status to such as "InProcess" or "Yes"')
    seq_id = parser.parse_args().seqid
    tenx_status = parser.parse_args().tenx_status
    main(seq_id, tenx_status)

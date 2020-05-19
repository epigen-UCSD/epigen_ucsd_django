#!/usr/bin/env python
import os
import sys
import django
import argparse
import subprocess
# print(os.path.abspath(__file__))

"""
This script should work for both scRNA snRNA and 10xATAC type experiment SingleCellObject models.
"""

basedir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(basedir))
sys.path.append(basedir)
sys.path.append(os.path.dirname(basedir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()

# Now this script or any imported module can use any part of Django it needs.
from masterseq_app.models import SeqInfo, LibraryInfo, SampleInfo
from singlecell_app.models import SingleCellObject, TenxqcInfo, scRNAqcInfo, CoolAdminSubmission
from singlecell_app.views import get_tenx_status, get_latest_modified_time
from django.contrib.auth.models import User
from django.conf import settings
from datetime import datetime
from populate_singlecell_objects import generate_qc_metrics_table

# hold all single cell experiment values
SINGLE_CELL_EXPS = ['10xATAC', 'scRNA-seq', 'snRNA-seq', 'scATAC-seq']

#These should be the only status's passed to the function. #TODO maybe add or force a check?
#No is the same status as ClickToSubmit 
status_types = ['Yes','No','InQueue','InProcess','Error!','ClickToSubmit']

def main(seq_id, status):
    # for example: python updateSingelCellStatus.py -sedid 'MM_130' -status 'InProcess'
    sc_obj = SingleCellObject.objects.get(seqinfo__seq_id=seq_id)
    sc_obj.tenx_pipeline_status = status
    if(status == 'Yes' or status == 'Error!'):
        sc_obj.date_last_modified = datetime.now()
    if(status == 'Yes'):
        #check if there is an error file that exists
        dir_to_expts = settings.TENX_DIR if sc_obj.experiment_type =="10xATAC" else settings.SCRNA_DIR
        error_file = sc_obj.experiment_type
        if()
        #make qc metrics table and save it to SCmodel's generic foreign key
        sc_obj.content_object = generate_qc_metrics_table(seq_id, sc_obj.experiment_type)
    sc_obj.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-seqid', help='Sequence Seq_id like MM_130')
    parser.add_argument('-status', help='Status to update to such as "InProcess" or "Yes"')
    seq_id = parser.parse_args().seqid
    status = parser.parse_args().status
    main(seq_id, status)

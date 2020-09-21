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
from singlecell_app.views import get_tenx_status, get_latest_modified_time, build_seq_list, get_group_name, get_seq_status, get_cooladmin_status
from django.contrib.auth.models import User, Group
from django.conf import settings
from datetime import datetime
from populate_singlecell_objects import generate_qc_metrics_table

# hold all single cell experiment values
SINGLE_CELL_EXPS = ['10xATAC', 'scRNA-seq', 'snRNA-seq', 'scATAC-seq']

# These should be the only status's passed to the function. #TODO maybe add or force a check?
# No is the same status as ClickToSubmit
status_types = ['Yes', 'No', 'InQueue', 'InProcess', 'Error!', 'ClickToSubmit']
cooladmin_objects = CoolAdminSubmission.objects.all()

def check_status(entry):
    #group_id = entry['libraryinfo__sampleinfo__group']
    #group_name = get_group_name(groups, group_id)
    #entry['libraryinfo__sampleinfo__group'] = group_name
    seq_id = entry['seq_id']
    experiment_type = entry['libraryinfo__experiment_type']
    entry['last_modified'] = get_latest_modified_time(
        seq_id, entry['id'], entry['date_submitted_for_sequencing'], cooladmin_objects)
    entry['seq_status'] = get_seq_status(seq_id, entry['read_type'])
    entry['10x_status'] = get_tenx_status(seq_id, experiment_type)
    entry['species'] = entry['libraryinfo__sampleinfo__species']
    entry['cooladmin_status'] = get_cooladmin_status(seq_id, entry['id'])
    return(entry)


def main():
    # get all sc seqs
    seqs_queryset = SeqInfo.objects.filter(libraryinfo__experiment_type__in=SINGLE_CELL_EXPS).select_related('libraryinfo', 'libraryinfo__sampleinfo', 'libraryinfo__sampleinfo__group').order_by(
        '-date_submitted_for_sequencing').values('id', 'seq_id', 'libraryinfo__experiment_type', 'read_type',
                                                 'libraryinfo__sampleinfo__species', 'date_submitted_for_sequencing', 'libraryinfo__sampleinfo__group', 'libraryinfo__sampleinfo__sample_id')
    print(len(seqs_queryset))  # 1444
    cooladmin_objects = CoolAdminSubmission.objects.all()
    groups = Group.objects.all()
    data = list(seqs_queryset)
    print(len(data))
    i = 0
    for entry in data:
        seq_obj = SeqInfo.objects.get(seq_id=entry['seq_id'])
        entry = check_status(entry)
        # seq_obj.save()
        sc_obj, created = SingleCellObject.objects.get_or_create(seqinfo=seq_obj,
                                                           date_last_modified=entry['date_submitted_for_sequencing'],
                                                           experiment_type=entry['libraryinfo__experiment_type'],
                                                           tenx_pipeline_status=entry['10x_status'])                                                           
        if(entry['10x_status'] == 'Yes'):
            try:
                sc_obj.content_object = generate_qc_metrics_table(
                    seq_obj.seq_id, sc_obj.experiment_type)
                sc_obj.save()
            except:
                a = 0
        if(created):
            print(i)
            sc_obj.save()
        i += 1

main()
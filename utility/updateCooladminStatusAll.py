#!/usr/bin/env python


import os
import sys
import django
import json
from django.conf import settings
from django.db.models.query import FlatValuesListIterable

# setting
basedir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(basedir))
sys.path.append(basedir)
sys.path.append(os.path.dirname(basedir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()

from singlecell_app.views import get_cooladmin_link, get_cooladmin_status
from masterseq_app.models import SeqInfo
from singlecell_app.models import SingleCellObject, CoolAdminSubmission
from datetime import datetime


coolAdminDir = settings.COOLADMIN_DIR

def getCoolAdminStatus(cool_obj):
  """
  get the cooladminstatus for the cooladminsubmission object
  """
  seq_id = cool_obj.seqinfo.seq_id 
  seq_dir =  os.path.join(coolAdminDir,seq_id)

  ## search for the final log file
  json_file = os.path.join(coolAdminDir,seq_id,'repl1','repl1_'+
  seq_id+'_final_logs.json')
     
  if not os.path.isfile(json_file): ## InQueue - is after click???
    cool_obj.pipeline_status="ClickToSubmit"
  else:
    with open(json_file,'r') as f:
      cool_data = f.read()
    cool_dict = json.loads(cool_data)
    cool_obj.submitted= True 
    cool_obj.link = cool_dict['report_address']
    #print(cool_dict["success"])
    cool_obj.pipeline_status = 'Yes' if cool_dict["success"] else 'failed'
  return cool_obj

def updateCoolAdminAll():
  """
  This function will scan cooladmin folder and update the db based on the folder's content
  """
  ## list all folders 
  seq_list = os.listdir(os.path.join(coolAdminDir))
  for seq in seq_list:
    print('reading library:'+seq)
    try:
      seq_obj = SeqInfo.objects.get(seq_id=seq)
      seq_obj.save()
      # print(seq.experiment_type)
      sc_obj, _ = SingleCellObject.objects.get_or_create(seqinfo=seq_obj)
      cool_sub_obj, _ = CoolAdminSubmission.objects.update_or_create(
          seqinfo=seq_obj)
      cool_sub_obj = getCoolAdminStatus(cool_sub_obj)
      cool_sub_obj.save()
      sc_obj.cooladminsubmission = cool_sub_obj
      sc_obj.date_last_modified = datetime.now()
      sc_obj.save()
      print('saving library:'+seq)
    except:
      print(seq+'not save')
      continue


if __name__ == '__main__':
    updateCoolAdminAll()

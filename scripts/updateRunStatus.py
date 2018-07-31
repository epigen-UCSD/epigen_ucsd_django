#!/usr/bin/env python
import os
import sys
import django
import argparse
#print(os.path.abspath(__file__))

os.chdir("../")
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()

from nextseq_app.models import RunInfo


def main():
	#for example: python updateRun.py -s '0' -f 'H5GLYBGX5fff'
	statuscode = {'-1':'ClickToSubmit','0':'JobSubmitted','1':'JobStarted','2':'Done','3': 'Error','4':'Warning'}
	parser = argparse.ArgumentParser()
	parser.add_argument('-s',choices=['-1','0','1','2','3','4'],\
		help = '-1: ClickToSubmit 0:JobSubmitted 1:JobStarted 2:Done 3:Error 4:Warning')
	parser.add_argument('-f',help = 'FlowCellID')
	thisstatus = parser.parse_args().s
	thisflowcellid = parser.parse_args().f
	#would not update 'Last Modified' column in this way
	#RunInfo.objects.filter(jobid=thisjobid).update(jobstatus=statuscode[thisstatus])
	obj=RunInfo.objects.get(Flowcell_ID=thisflowcellid)
	obj.jobstatus=statuscode[thisstatus]
	obj.save()


if __name__ == '__main__':
	main()
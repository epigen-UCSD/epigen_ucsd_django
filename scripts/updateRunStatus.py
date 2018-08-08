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
	#for example: python updateRunStatus.py -s '0' -f 'H5GLYBGX5fff'
	#if you have dir to save, python updateRunStatus.py -s '0' -d '/Users/180705_AH5GLYBGX5431' -f 'H5GLYBGX5fff'
	statuscode = {'-1':'ClickToSubmit','0':'JobSubmitted','1':'JobStarted','2':'Done','3': 'Error','4':'Warning'}
	parser = argparse.ArgumentParser()
	parser.add_argument('-s',choices=['-1','0','1','2','3','4'],\
		help = '-1: ClickToSubmit 0:JobSubmitted 1:JobStarted 2:Done 3:Error 4:Warning')
	parser.add_argument('-f',help = 'FlowCellID')
	parser.add_argument('-d',help = 'Nextseq Dir')
	thisstatus = parser.parse_args().s
	thisflowcellid = parser.parse_args().f
	thisdir = ''
	try:
		thisdir = parser.parse_args().d
	except:
		pass
	#would not update 'Last Modified' column in this way
	#RunInfo.objects.filter(jobid=thisjobid).update(jobstatus=statuscode[thisstatus])
	obj=RunInfo.objects.get(Flowcell_ID=thisflowcellid)
	obj.jobstatus=statuscode[thisstatus]
	if thisdir:
		obj.nextseqdir = thisdir
	obj.save()


if __name__ == '__main__':
	main()

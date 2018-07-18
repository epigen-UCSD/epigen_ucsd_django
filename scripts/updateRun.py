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
	#for example: python updateRun.py -s '0' -j '12345'
	statuscode = {'-1':'ToSubmit','0':'JobSumitted','1':'JobStarted','2':'Done'}
	parser = argparse.ArgumentParser()
	parser.add_argument('-s',choices=['-1','0','1','2'],help = '-1: ToSubmit 0:JobSumitted 1:JobStarted 2:Done')
	parser.add_argument('-j',help = 'jobid')
	thisstatus = parser.parse_args().s
	thisjobid = parser.parse_args().j
	#would not update 'Last Modified' column in this way
	#RunInfo.objects.filter(jobid=thisjobid).update(jobstatus=statuscode[thisstatus])
	obj=RunInfo.objects.get(jobid=thisjobid)
	obj.jobstatus=statuscode[thisstatus]
	obj.save()


if __name__ == '__main__':
	main()
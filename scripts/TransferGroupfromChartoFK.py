#!/usr/bin/env python
import os
import sys
import django
import argparse
import datetime

#os.chdir("../")
basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()

from masterseq_app.models import SampleInfo
from django.contrib.auth.models import Group

def main():
	for sample in SampleInfo.objects.all():
		if sample.group:
			print(sample.group)
			sample.group_tm = Group.objects.get(name=sample.group.replace(' ','_')+'_group')
			sample.save()

if __name__ == '__main__':
	main()
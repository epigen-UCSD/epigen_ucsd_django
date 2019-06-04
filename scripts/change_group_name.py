#!/usr/bin/env python
import os
import sys
import django
import argparse
import datetime
import secrets
import string

#print(os.path.abspath(__file__))

os.chdir("../")
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()

from django.contrib.auth.models import Group


def main():

	for i in Group.objects.all():
		gname = i.name
		if gname =='Ch_Pilot_Project_group':
			gname_tm = ' '.join(gname.split('_')[0:3])
		else:
			gname_tm = ' '.join(gname.split('_')[0:2])
		if ' group' in gname_tm:
			gname_tm = ' '.join(gname_tm.split(' ')[0:-1])
		print(gname_tm)
		i.name = gname_tm
		i.save()

if __name__ == '__main__':
	main()
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

from django.contrib.auth.models import Group,User

def main():
	groupUser = {}
	with open('./groupUsers.cfg','r') as f:
		for line in f:
			fields = line.strip('\n')
			print(fields)
			if fields.startswith('#'):
				thisgroup = fields.rstrip(':').lstrip('#')
				obj, created = Group.objects.get_or_create(name=thisgroup)
				obj.user_set.clear()
			elif fields:
				thisgroupuser = User.objects.get(username=fields)
				obj.user_set.add(thisgroupuser)


if __name__ == '__main__':
	main()

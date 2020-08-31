#!/usr/bin/env python

import os
import sys
import django
import io

os.chdir("../")
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()
from collaborator_app.models import ServiceRequest


def main():

	with open('utility/quote_import.tsv','r') as f:
		for line in f:
			fields = line.strip('\n').split('\t')
			if '/' in fields[0]:
				group_name = fields[0].split('/')[0].strip()
				contact = fields[0].split('/')[1].strip()
			else:
				group_name = fields[0].strip()
				contact = ''
			a = fields[2]
			this_date = '20'+a[4:6]+'-'+a[0:2]+'-'+a[2:4]
			this_quote = fields[3]
			this_amount = fields[4]
			obj, created = ServiceRequest.objects.get_or_create(quote_number=[this_quote],quote_amount=[this_amount],date=this_date,group=group_name,research_contact=contact)


if __name__ == '__main__':
    main()

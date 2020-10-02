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
from collaborator_app.models import ServiceInfo


def main():

	with open('utility/rate_table.tsv','r') as f:
		next(f)
		for line in f:
			fields = line.strip('\n').split('\t')
			this_service = fields[0].strip()
			uc = float(''.join(fields[1].strip('$').split(',')))
			non_uc = float(''.join(fields[3].strip('$').split(',')))
			industry = float(''.join(fields[5].strip('$').split(',')))
			unit = fields[7].strip('')
			brief = fields[8].strip('')
			detail = fields[9].strip('')

			ServiceInfo.objects.create(service_name=this_service,uc_rate=uc,nonuc_rate=non_uc,industry_rate=industry,rate_unit=unit,description_brief=brief,description=detail)
			if fields[2]:
				this_service = fields[0].strip()+'(passthrough)'
				uc = float(''.join(fields[2].strip('$').split(',')))
				non_uc = float(''.join(fields[4].strip('$').split(',')))
				industry = float(''.join(fields[6].strip('$').split(',')))
				unit = fields[7].strip('')
				ServiceInfo.objects.create(service_name=this_service,uc_rate=uc,nonuc_rate=non_uc,industry_rate=industry,rate_unit=unit)

				this_service = fields[0].strip()+'(pilot)'
				uc = float(''.join(fields[1].strip('$').split(',')))
				non_uc = float(''.join(fields[3].strip('$').split(',')))
				industry = float(''.join(fields[5].strip('$').split(',')))
				unit = fields[7].strip('')
				ServiceInfo.objects.create(service_name=this_service,uc_rate=uc,nonuc_rate=non_uc,industry_rate=industry,rate_unit=unit)


if __name__ == '__main__':
    main()

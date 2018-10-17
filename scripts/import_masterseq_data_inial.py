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

from masterseq_app.models import SampleInfo

def main():
	print("beginning")
	active_index = []
	active_index_2 = []
	with open('scripts/MSTS_Active.tsv','r') as f:
		next(f)
		next(f)
		next(f)
		for line in f:
			fields = line.split('\t')
			if fields[8]:
				if fields[12].split('(')[0].strip() == 'FACS sorted cells' or fields[12].split('(')[0].strip() == 'douncing homogenization':
					preparation_tm = 'other'
					note_tm = ';'.join([fields[28].strip(),fields[12].split('(')[0].strip()]).strip(';')

				elif fields[12].split('(')[0].strip() == 'flash frozen':
					preparation_tm = 'flash frozen without cryopreservant'
					note_tm = fields[28].strip()
				else:
					preparation_tm = fields[12].split('(')[0].strip()
					note_tm = fields[28].strip()
				active_index.append(fields[21].strip())
				active_index_2.append(fields[21].strip())

				obj,created = SampleInfo.objects.get_or_create(
					sample_id = fields[8].strip(),
					sample_index = fields[21].strip(),
					species = fields[10].split('(')[0].lower().strip(),
					sample_type = fields[11].split('(')[0].strip(),
					preparation = preparation_tm,
					description = fields[9].strip(),
					notes = note_tm,
				)

	with open('scripts/MSTS.tsv','r') as f:
		next(f)
		next(f)
		next(f)
		for line in f:
			fields = line.split('\t')
			if fields[8] and not fields[21].strip() in active_index:
				active_index_2.append(fields[21].strip())
				if fields[12].split('(')[0].strip() == 'FACS sorted cells' or fields[12].split('(')[0].strip() == 'douncing homogenization':
					preparation_tm = 'other'
					note_tm = ';'.join([fields[28].strip(),fields[12].split('(')[0].strip()]).strip(';')

				elif fields[12].split('(')[0].strip() == 'flash frozen':
					preparation_tm = 'flash frozen without cryopreservant'
					note_tm = fields[28].strip()
				else:
					preparation_tm = fields[12].split('(')[0].strip()
					note_tm = fields[28].strip()

				obj,created = SampleInfo.objects.get_or_create(
					sample_id = fields[8].strip(),
					sample_index = fields[21].strip(),
					species = fields[10].split('(')[0].lower().strip(),
					sample_type = fields[11].split('(')[0].strip(),
					preparation = preparation_tm,
					description = fields[9].strip(),
					notes = note_tm,
				)
	print(SampleInfo.objects.count())





if __name__ == '__main__':
	main()
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

from masterseq_app.models import SequencingInfo

def main():
	#for example: python mseqinfoimport.py -i 'scripts/MSeqTS.tsv'
	parser = argparse.ArgumentParser()
	parser.add_argument('-i',help = 'MSeqTS.tsv file')
	mseqtsfile = parser.parse_args().i
	print(mseqtsfile)
	with open(mseqtsfile,'r') as f:
		for line in f:
			fields = line.split('\t')
			if len(fields) < 8 or fields[8] == 'Sequencing ID':
				continue
			if fields[8] != '':
				obj,created = SequencingInfo.objects.get_or_create(sequencing_id=fields[8])
	print(SequencingInfo.objects.count())



if __name__ == '__main__':
	main()
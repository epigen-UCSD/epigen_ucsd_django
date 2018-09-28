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

from nextseq_app.models import RunInfo,LibrariesInRun

def main():
	#for example: python saveReadsNumber.py -i 'scripts/readsnumber.tsv'
	parser = argparse.ArgumentParser()
	parser.add_argument('-i',help = 'inputfile for reads number')
	readsnumberfile = parser.parse_args().i
	print(readsnumberfile)
	with open(readsnumberfile,'r') as f:
		for line in f:
			fields = line.strip('\n').split('\t')
			obj = LibrariesInRun.objects.get(Library_ID=fields[0])
			obj.numberofreads = int(fields[1])
			obj.save()



if __name__ == '__main__':
	main()




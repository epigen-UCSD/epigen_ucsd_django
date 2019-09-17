#!/usr/bin/env python
import os
import sys
import django
import re

#print(os.path.abspath(__file__))

os.chdir("../")
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()
from masterseq_app.models import SeqInfo
from nextseq_app.models import Barcode

def main():
	file = 'scripts/seq_i7index_20190904'

	with open(file,'r') as f:
		for line in f:
			fields = line.strip('\n').split('\t')
			#print(fields[0])
			currentseq = SeqInfo.objects.get(seq_id=fields[0])
			if fields[1]:
				currentseq.i7index = Barcode.objects.get(indexid=fields[1])
			else:
				currentseq.i7index = None
			currentseq.save()




if __name__ == '__main__':
	main()




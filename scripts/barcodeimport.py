#!/usr/bin/env python
import os
import sys
#print(os.path.abspath(__file__))
basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")

import django
django.setup()
from nextseq_app.models import Barcode

def main():
	
	index = {}
	i= 0
	with open('barcodes.csv','r') as f:
		for line in f:
			fields = line.strip('\n').split('\t')
			if fields[0] in index.keys():
				if fields[0]!= index[fields[0]]:
					print(fields[0]+' sequence conflict!')
					sys.exit()
			else:
				index[fields[0]] = fields[1]
				i += 1
		print(i)
	#tobecreatedlist = []
	for item in index.keys():
		#tobecreatedlist.append(Barcode(indexid=item, indexseq=index[item]))
		Barcode.objects.get_or_create(indexid=item, indexseq=index[item])
	#Barcode.objects.bulk_create(tobecreatedlist)
	#Barcode.objects.all().delete()



if __name__ == '__main__':
	main()

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

def getReadNumber(lib):
        '''
        get number of reads for input lib
        '''
        

def main():
	#for example: python saveReadsNumber.py -f 'xxx|flowcellid'
	parser = argparse.ArgumentParser()
	parser.add_argument('-f',help = 'flowcell id')
	flowcell = parser.parse_args().f
        obj=LibrariesInRun.objects.get(singlerun=flowcell)
        libs= [s.Library_ID  for s in obj.librariesinrun_set.all()]
        
	print(readsnumberfile)
	with open(readsnumberfile,'r') as f:
		for line in f:
			fields = line.strip('\n').split('\t')
			obj = LibrariesInRun.objects.get(Library_ID=fields[0])
			obj.numberofreads = int(fields[1])
			obj.save()



if __name__ == '__main__':
	main()




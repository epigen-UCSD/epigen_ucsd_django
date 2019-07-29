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
from masterseq_app.models import LibraryInfo

def main():
	file_active = 'scripts/ts2_active_0729_for_libdescrip_import.tsv'
	file_archived = 'scripts/ts2_archived_0729_for_libdescrip_import.tsv'
	alllibs = []
	writeline = []
	errfile = 'scripts/import_lib_description.err'

	with open(file_active,'r') as f:
		next(f)
		next(f)
		next(f)
		for line in f:
			fields = line.strip('\n').split('\t')
			if fields[10]:
				fields[10] = fields[10].replace('-','_')
				alllibs.append(fields[10].strip()+':'+fields[12].strip())
				lib_desc = 
				try:
					thislib = LibraryInfo.get(library_id=fields[10],experiment_index=fields[12].strip())
					thislib.library_description = 
				except:
					print(fields[10].strip()+':'+fields[12].strip())
					writeline.append(fields[10].strip()+':'+fields[12].strip())

	with open(file_active,'r') as f:
		next(f)
		next(f)
		next(f)
		for line in f:
			fields = line.strip('\n').split('\t')
			if fields[10]:
				fields[10] = fields[10].replace('-','_')
				if fields[10].strip()+':'+fields[12].strip() not in alllibs:
					alllibs.append(fields[10].strip()+':'+fields[12].strip())
					try:
						thislib = LibraryInfo.get(library_id=fields[10],experiment_index=fields[12].strip())
					except:
						print(fields[10].strip()+':'+fields[12].strip())
						writeline.append(fields[10].strip()+':'+fields[12].strip())

	with open(errfile,'w') as fw:
		fw.write('\n'.join(writeline))
		fw.write('\n')





if __name__ == '__main__':
	main()




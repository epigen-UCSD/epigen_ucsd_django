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

from setqc_app.models import LibrariesSetQC
from django.contrib.auth.models import User
from masterseq_app.models import SequencingInfo

def libraryparse(libraries):
	tosave_list = []
	for library in libraries.split(','):
		librarytemp = library.replace('\xe2\x80\x93','-').replace('\xe2\x80\x94','-').split('-')
		if len(librarytemp) > 1:
			prefix = librarytemp[0].strip().split('_')[0]
			try:
				suffix = librarytemp[0].strip().split('_',2)[2]
			except IndexError as e:
				#print(e)
				suffix = ''
			startlib = librarytemp[0].strip().split('_')
			endlib = librarytemp[1].strip().split('_')
			if len(startlib) == len(endlib):
				numberrange = [startlib[1],endlib[1]]
			else:
				numberrange =[startlib[1],endlib[0]]
			if int(numberrange[1])<int(numberrange[0]):
				raise forms.ValidationError('Please check the order: '+ library)
			if not suffix:
				tosave_list += ['_'.join([prefix,str(x)]) for x in range(int(numberrange[0]),int(numberrange[1])+1)]
			else:
				tosave_list += ['_'.join([prefix,str(x),suffix]) for x in range(int(numberrange[0]),int(numberrange[1])+1)]
		else:
			tosave_list.append(library.strip())

	return tosave_list

def main():
	#for example: python setqcimport.py -i 'scripts/MSQcTS.tsv'
	parser = argparse.ArgumentParser()
	parser.add_argument('-i',help = 'setQC.tsv file')
	setqcfile = parser.parse_args().i
	print(setqcfile)
	ignorline = ('IMPORTANT NOTE','To be completed','Date requested')
	with open(setqcfile,'r') as f:
		for line in f:
			fields = line.strip('\n').strip('\s').split('\t')
			if len(fields) > 8 and fields[0] > '2018-07-18' and not fields[0].startswith(ignorline):
				print(fields)
				setinfo,created = LibrariesSetQC.objects.get_or_create(set_name=fields[2],setID=fields[7],\
					date_requested=fields[0],experiment_type=fields[3].split('(')[0],notes=fields[5],\
					url=fields[6],requestor=User.objects.get(username=fields[1]))

				tosave_librarylist = libraryparse(fields[4])
				for item in tosave_librarylist:
					if item:
						setinfo.libraries_to_include.add(SequencingInfo.objects.get(sequencing_id=item))

if __name__ == '__main__':
	main()
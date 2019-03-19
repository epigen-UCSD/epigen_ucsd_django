#!/usr/bin/env python
import os
import sys
import django
import argparse
import datetime
#print(os.path.abspath(__file__))

os.chdir("../")
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()

from masterseq_app.models import SeqInfo,GenomeInfo
from setqc_app.models import LibrariesSetQC,LibraryInSet
from django.contrib.auth.models import User
from django.conf import settings
import re

defaultgenome = {'human': 'hg38', 'mouse': 'mm10', 'rat': 'rn6'}

def datetransform(inputdate):
	#from 2/6/2018 to 2018-02-06
	if inputdate.strip() in ['N/A','NA','']:
		return None
	elif '-' in inputdate.strip():
		return inputdate.strip()
	else:
		tm = inputdate.strip().split('/')
		year = tm[2].strip()
		month = tm[0].strip().zfill(2)
		date = tm[1].strip().zfill(2)
		if len(year) == 2:
			year = '20'+year
		return '-'.join([year,month,date])
def libraryparse(libraries):
	tosave_list = []
	for library in libraries.split(','):
		librarytemp = library.replace(
			'\xe2\x80\x93', '-').replace('\xe2\x80\x94', '-').split('-')
		#print(librarytemp)
		if len(librarytemp) > 1:
			prefix = librarytemp[0].strip().split(
				'_')[0] if '_' in librarytemp[0] else ''
			try:
				suffix = librarytemp[0].strip().split('_', 2)[2]  # force strip up to 3 pieces
			except IndexError as e:
				print(e)
				suffix = ''
			startlib = librarytemp[0].strip().split('_')
			endlib = librarytemp[1].strip().split('_')
			if len(startlib) == len(endlib) > 1:  # 'JYH_1-JYH_3'
				numberrange = [startlib[1], endlib[1]]
			elif len(startlib) == len(endlib) == 1:  # '1-3'
				numberrange = [startlib[0], endlib[0]]
			else:  # 'JYH_1-3'
				numberrange = [startlib[1], endlib[0]]
			if int(numberrange[1]) < int(numberrange[0]):
				raise forms.ValidationError(
					'Please check the order: ' + library)
			if not suffix and prefix:
				tosave_list += ['_'.join([prefix, str(x)])
								for x in range(int(numberrange[0]), int(numberrange[1])+1)]
			elif not suffix:
				tosave_list += [str(x)
								for x in range(int(numberrange[0]), int(numberrange[1])+1)]
			else:
				tosave_list += ['_'.join([prefix, str(x), suffix])
								for x in range(int(numberrange[0]), int(numberrange[1])+1)]
		else:
			tosave_list.append(library.strip())
	return list(sorted(set(tosave_list)))


def main():
	setqcoutdir = settings.SETQC_DIR
	print(setqcoutdir)
	setqcfile = ['scripts/TS5_Archived.tsv','scripts/TS5_Active.tsv']
	

	for files in setqcfile:
		print('from file: '+ files)
		with open(files,'r') as f:
			next(f)
			next(f)
			next(f)
			for line in f:
				tosave_list = []
				fields = line.split('\t')
				set_id = fields[7].strip()
				set_date = datetransform(fields[0].strip())
				note_tm = fields[5].strip()
				exp_tm = fields[3].strip()
				try:
					username_tm = fields[1].strip()
					if username_tm == 'RM':
						username_tm = 'RMM'
					teammember = User.objects.get(username = username_tm)
				except:
					print('NO Requestor, assigned to ZC')
					teammember = User.objects.get(username = 'ZC')
					if fields[1].strip()!='' and not fields[1].strip().lower().startswith('other'):					
						note_tm = ';'.join([note_tm,'Requestor recorded in TS5:'+fields[1].strip()]).strip(';')
			
				#librariestoinclude = []
				#librariestoinclude = libraryparse(fields[4].strip())
				# for item in librariestoinclude:
				# 	if item:
				# 		if not SeqInfo.objects.filter(seq_id=item).exists():
				# 			print(fields[7].strip()+':'+item)	


				if set_date < '2018-11-14':
					print(set_id)
					#print(fields[1].strip())


					# if not LibrariesSetQC.objects.filter(set_id = fields[7].strip()).exists():
					# 	print(fields[7].strip())
					#print(teammember)
					obj,created = LibrariesSetQC.objects.get_or_create(
						set_id = fields[7].strip(),
						requestor = teammember,
						)
					obj.set_name = fields[2].strip()
					obj.date_requested = set_date
					obj.experiment_type = fields[3].strip()
					obj.notes = note_tm
					try:
						obj.comments = fields[11].strip()
					except Exception as e:
						print(e)
					obj.url = fields[6].strip()
					try:
						obj.version =  fields[10].strip()
					except Exception as e:
						print(e)
					obj.status = 'Done'
					obj.save()
					#obj.libraries_to_include.clear()
					
					if set_id in ['Set_24','Set_25','Set_26','Set_51','Set_89','Set_135','Set_156','Set_164','Set_181','Set_187','Set_185','Set_193']:
						librariestoinclude = libraryparse(fields[4].strip())
						#print(librariestoinclude)
						for item in librariestoinclude:
							if item:
								#print(item)

								seqinfo_tm = SeqInfo.objects.get(seq_id=item)
								speci = seqinfo_tm.libraryinfo.sampleinfo.species
								genome_tm = defaultgenome[speci]
								tosave_item = LibraryInSet(
									librariesetqc=obj,
									seqinfo=seqinfo_tm,
									label=seqinfo_tm.default_label,
									genome=GenomeInfo.objects.get(genome_name=genome_tm),
								)
								tosave_list.append(tosave_item)
					else:
						with open(os.path.join(setqcoutdir,set_id+'.txt'),'r') as ff:
							for line_ff in ff:
								#fields_ff = line_ff.strip('\n').split('')
								fields_ff = re.split(r'[\s]+', line_ff.strip('\n'))
								if fields_ff[0].strip():
									#print(fields_ff[0])
									seqinfo_tm = SeqInfo.objects.get(seq_id=fields_ff[0].strip())
									speci = seqinfo_tm.libraryinfo.sampleinfo.species
									genome_tm = defaultgenome[speci]	
									if exp_tm != 'ChIP-seq':
										tosave_item = LibraryInSet(
											librariesetqc=obj,
											seqinfo=seqinfo_tm,
											label=seqinfo_tm.default_label,
											genome=GenomeInfo.objects.get(genome_name=genome_tm),
										)
										tosave_list.append(tosave_item)			
									else:
										if set_id in ['Set_70','Set_96','Set_70_test','Set_101','Set_113','Set_120','Set_126','Set_182','Set_184','Set_186','Set_188','Set_189','Set_190']:
											group_tm = '1'
											isinput_tm = 'False'
										else:
											#print(fields_ff[2])
											group_tm = fields_ff[1].strip()
											isinput_tm = fields_ff[2].strip().title()
											if not isinput_tm in ['False','True']:
												print('fields are separated not right!')
										tosave_item = LibraryInSet(
											librariesetqc=obj,
											seqinfo=seqinfo_tm,
											label=seqinfo_tm.default_label,
											genome=GenomeInfo.objects.get(genome_name=genome_tm),
											group_number=group_tm,
											is_input=isinput_tm,			

											)
										tosave_list.append(tosave_item)	
						#print(tosave_list)
					LibraryInSet.objects.bulk_create(tosave_list)
						
				else:
					setobj = LibrariesSetQC.objects.get(set_id = fields[7].strip())
					setobj.requestor = teammember
					setobj.save()








if __name__ == '__main__':
	main()
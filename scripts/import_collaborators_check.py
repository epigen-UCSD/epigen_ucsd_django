#!/usr/bin/env python
import os
import sys
import django
import argparse
import datetime
import secrets
import string


os.chdir("../")
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()

from masterseq_app.models import SampleInfo
from django.contrib.auth.models import Group,User
from epigen_ucsd_django.models import CollaboratorPersonInfo

def parsename(namestring):
	#return list of [username, firstname, lastname]
	namesep = namestring.split(' ')
	if len(namesep) == 1:
		return [namestring.lower(),'',namestring.capitalize()]
	elif len(namesep) == 2:
		return [(namesep[0][0]+namesep[1]).lower(),namesep[0].capitalize(),namesep[1].capitalize()]
	elif len(namesep) == 3:
		return [(namesep[0][0]+namesep[2]).lower(),namesep[0].capitalize(),namesep[2].capitalize()]
	else:
		return False


def main():
	alphabet = string.ascii_letters + string.digits
	writeline = []
	groupbelong = {}
	assignedsamp = []
	sampfiles = ['scripts/TS1_Archived_201904.tsv','scripts/TS1_Active_201904.tsv']
	for file in sampfiles:
		print(file)
		with open(file,'r') as f:
			next(f)
			next(f)
			next(f)
			for line in f:
				fields = line.split('\t')
				if fields[0] and fields[1] and fields[1] not in ['N/A','Coriell','Joe Gleeson']:
					sampindex = fields[21].strip()
					if not sampindex in assignedsamp:
						if not SampleInfo.objects.filter(sample_index=sampindex).exists():
							print(sampindex+' not stored in database!')
							#exit()
						else:
							if SampleInfo.objects.filter(sample_index=sampindex).count()>1:
								print(sampindex+' duplicate in database!')
								#exit()
							else:
								sampinfo = SampleInfo.objects.get(sample_index=sampindex)
								piname = fields[1].strip()
								researchname = fields[2].strip()
								fiscalname = fields[5].strip()
								#print(researchname)
								if researchname not in ['NA','N/A','Wen Yan'] and researchname:
									if researchname in groupbelong.keys():	

										if piname != groupbelong[researchname]:
											print(researchname+' duplicate!(in different group).Please correct it because the username should be unique')
											print(piname+' vs '+groupbelong[researchname])
											#exit()
									else:
										groupbelong[researchname] = piname
								if fiscalname not in ['NA','N/A'] and fiscalname:
									if fiscalname in groupbelong.keys():
										if piname != groupbelong[fiscalname]:
											print(fiscalname+' duplicate!(in different group).Please correct it because the username should be unique')
											print(piname+' vs '+groupbelong[fiscalname])
											#exit()
									else:
										groupbelong[fiscalname] = piname		

								group_name = '_'.join([x for x in piname.title().split(' ')])+'_group'
								#print(group_name)
								if fields[1].strip() == 'Arima':
									piname = 'Siddarth Selvaraj'
								if fields[1].strip() == 'Pfizer':
									piname = 'Thomas Paul'
								if fields[1].strip() == 'Tempus':
									piname = 'Kevin White'
								if fields[1].strip() == 'CH_Pilot_Project':
									piname = 'Calvin Yeang'

								pinameparse = parsename(piname)
								if pinameparse:
									passwordrand = ''.join(secrets.choice(alphabet) for i in range(10))
									
								else:
									print('PI name:'+piname+' can not parse!')	
			

								resnameparse = parsename(researchname)
								if resnameparse:
									passwordrand = ''.join(secrets.choice(alphabet) for i in range(10))
								else:
									print('Research name:'+researchname+' can not parse!')	
			

								fisnameparse = parsename(fiscalname)
								if fisnameparse:
									passwordrand = ''.join(secrets.choice(alphabet) for i in range(10))
								else:
									print('Fiscal name:'+fiscalname+' can not parse!')
								assignedsamp.append(sampindex)

								if int(sampindex.split('-')[1])<830:
									if group_name!='David_Gorkin_group':
										try:
											Group.objects.get(name=group_name)
										except:
											print('Error in getting group:'+group_name+'!'+sampindex)
											exit()
									if pinameparse and piname not in ['','NA','N/A','David Gorkin']:
										try:
											User.objects.get(username=pinameparse[0],first_name=pinameparse[1],last_name=pinameparse[2])
										except:
											print('Error in getting pi user:'+piname+'!'+sampindex)
											exit()
									if resnameparse and researchname not in ['','NA','N/A']:
										try:
											User.objects.get(username=resnameparse[0],first_name=resnameparse[1],last_name=resnameparse[2])
										except:
											print('Error in getting research user:'+researchname+'!'+sampindex)
											exit()
									if fisnameparse and fiscalname not in ['','NA','N/A','Truc Dang']:
										try:
											User.objects.get(username=fisnameparse[0],first_name=fisnameparse[1],last_name=fisnameparse[2])
										except:
											print('Error in getting fiscal user:'+fiscalname+'!'+sampindex)
											exit()
	print('the end!')	


if __name__ == '__main__':
	main()
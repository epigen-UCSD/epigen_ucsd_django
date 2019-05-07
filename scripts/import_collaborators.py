#!/usr/bin/env python
import os
import sys
import django
import argparse
import datetime
import secrets
import string

#print(os.path.abspath(__file__))

os.chdir("../")
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()

from masterseq_app.models import SampleInfo
from django.contrib.auth.models import Group,User
from epigen_ucsd_django.models import CollaboratorPersonInfo,Person_Index

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
				if fields[0] and fields[1] and fields[1] not in ['NA','N/A']:
					sampindex = fields[21].strip()
					if not sampindex in assignedsamp:
						if not SampleInfo.objects.filter(sample_index=sampindex).exists():
							print(sampindex+' not stored in database!')
						else:
							sampinfo = SampleInfo.objects.get(sample_index=sampindex)
							piname = fields[1].strip()							
							researchname = fields[2].strip()
							fiscalname = fields[5].strip()	
							group_name = '_'.join([x for x in piname.title().split(' ')])+'_group'
							#print(group_name)							
							objgroup, created = Group.objects.get_or_create(name=group_name)
							sampinfo.group = objgroup
							if fields[1].strip() == 'Arima':
								piname = 'Siddarth Selvaraj'
							if fields[1].strip() == 'Pfizer':
								piname = 'LSA'
								fiscalname = 'Stephanie Shi'
							if fields[1].strip() == 'Tempus':
								piname = 'Kevin White'
							if fields[1].strip() == 'CH_Pilot_Project':
								piname = 'Calvin Yeang'
							nameparse = parsename(piname)
							if nameparse:
								passwordrand = ''.join(secrets.choice(alphabet) for i in range(10))
								if not User.objects.filter(username=nameparse[0]).exists():
									piaccount = User.objects.create_user(
										username = nameparse[0],
										first_name = nameparse[1],
										last_name = nameparse[2],
										password = passwordrand,
										)
									objgroup.user_set.add(piaccount)
									piperson = CollaboratorPersonInfo.objects.create(
										person_id = piaccount,
										role = 'PI'
										)
									writeline.append('\t'.join([objgroup.name,nameparse[0],passwordrand,nameparse[1],nameparse[2]]))
								else:
									piaccount = User.objects.get(username=nameparse[0])
									piperson = CollaboratorPersonInfo.objects.get(person_id=piaccount)
									piperson.role='PI'
									piperson.fiscal_index=None
									piperson.save()
									#writeline.append('\t'.join([objgroup.name,piaccount.username,piaccount.password,piaccount.first_name,piaccount.last_name]))
		
							nameparse = parsename(researchname)
							if nameparse:
								if researchname and researchname not in ['NA','N/A']:
									if fields[4].strip() not in ['NA','N/A']:
										phone_tm = fields[4].strip()
									else:
										phone_tm = None
									passwordrand = ''.join(secrets.choice(alphabet) for i in range(10))
									if not User.objects.filter(username=nameparse[0]).exists():
										researchaccount = User.objects.create_user(
											username = nameparse[0],
											first_name = nameparse[1],
											last_name = nameparse[2],
											password = passwordrand,
											email = fields[3].strip()
											)
										objgroup.user_set.add(researchaccount)
										researchperson = CollaboratorPersonInfo.objects.create(
											person_id = researchaccount,
											cell_phone = phone_tm,
											role = 'other'
											)
										writeline.append('\t'.join([objgroup.name,nameparse[0],passwordrand,nameparse[1],nameparse[2]]))										
									else:
										researchaccount = User.objects.get(username=nameparse[0])
										researchperson = CollaboratorPersonInfo.objects.get(person_id=researchaccount)
										if researchname!=piname:
											researchperson.role='other'
										else:
											researchperson.role='PI'
										researchperson.fiscal_index=None
										researchperson.cell_phone=phone_tm
										researchperson.save()
										#writeline.append('\t'.join([objgroup.name,researchaccount.username,researchaccount.password,researchaccount.first_name,researchaccount.last_name]))
									sampinfo.research_person = researchperson	
		
							nameparse = parsename(fiscalname)
							if nameparse:
								if fiscalname and fiscalname not in ['NA','N/A']:
									passwordrand = ''.join(secrets.choice(alphabet) for i in range(10))
									if not User.objects.filter(username=nameparse[0]).exists():
										fiscalaccount = User.objects.create_user(
											username = nameparse[0],
											first_name = nameparse[1],
											last_name = nameparse[2],
											password = passwordrand,
											email = fields[6].strip()
											)
										objgroup.user_set.add(fiscalaccount)
										fiscalperson = CollaboratorPersonInfo.objects.create(
											person_id = fiscalaccount,
											role = 'other'
											)
										writeline.append('\t'.join([objgroup.name,nameparse[0],passwordrand,nameparse[1],nameparse[2]]))										
									else:
										fiscalaccount = User.objects.get(username=nameparse[0])
										fiscalperson=CollaboratorPersonInfo.objects.get(person_id=fiscalaccount)
										if fiscalname!=piname:
											fiscalperson.role='other'
										else:
											fiscalperson.role='PI'

										fiscalperson.fiscal_index=None
										fiscalperson.save()
										#writeline.append('\t'.join([objgroup.name,fiscalaccount.username,fiscalaccount.password,fiscalaccount.first_name,fiscalaccount.last_name]))
		
									index_tm = fields[7].strip()
									if index_tm not in ['','NA','N/A','other']:
										index_tm = fields[7].strip()
									else:
										index_tm = ''
									fisperson_index, created = Person_Index.objects.get_or_create(
										person=fiscalperson,
										index_name=index_tm,
										)
									sampinfo.fiscal_person_index = fisperson_index
								else:
									if fields[7].strip() not in ['','NA','N/A','other']:
										fisperson_index, created = Person_Index.objects.get_or_create(
											person=None,
											index_name=index_tm,
										)
										sampinfo.fiscal_person_index = fisperson_index										

							sampinfo.fiscal_person = None
							sampinfo.save()
							assignedsamp.append(sampindex)
	writeline_final = []
	for item in writeline:
		fields = item.split('\t')		
		person_tm = CollaboratorPersonInfo.objects.get(person_id=User.objects.get(username=fields[1]))
		writeline_final.append('\t'.join([fields[0],person_tm.role]+fields[1:]))
	with open('scripts/collaboratorpassword_new.tsv','w') as fw:
		fw.write('\t'.join(['group','role','username','password','firstname','lastname']))
		fw.write('\n')
		fw.write('\n'.join(writeline_final))
		fw.write('\n')


if __name__ == '__main__':
	main()
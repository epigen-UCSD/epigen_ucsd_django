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
from epigen_ucsd_django.models import CollaboratorPersonInfo

def parsename(namestring):
	#return list of [username, firstname, lastname]
	namesep = namestring.split(' ')
	if len(namesep) == 1:
		return [namestring.lower(),'',namestring.lower()]
	elif len(namesep) == 2:
		return [(namesep[0][0]+namesep[1]).lower(),namesep[0],namesep[1]]
	else:
		return False


def main():
	alphabet = string.ascii_letters + string.digits
	writeline = []
	groupbelong = {}
	assignedsamp = []
	sampfiles = ['scripts/MSTS.tsv','scripts/MSTS_Active.tsv']
	for file in sampfiles:
		with open(file,'r') as f:
			next(f)
			next(f)
			next(f)
			for line in f:
				fields = line.split('\t')
				if fields[0] and fields[1] and fields[1]!='N/A':
					sampindex = fields[21].strip()
					if not sampindex in assignedsamp:
						if not SampleInfo.objects.filter(sample_index=sampindex).exists():
							print(sampindex+' not stored in database!')
						else:
							if SampleInfo.objects.filter(sample_index=sampindex).count()>1:
								print(sampindex+' duplicate in database!')
							else:
								sampinfo = SampleInfo.objects.get(sample_index=sampindex)
								piname = fields[1].strip()
								researchname = fields[2].strip()
								fiscalname = fields[5].strip()
								#print(researchname)
								if researchname not in ['NA','N/A'] and researchname:
									if researchname in groupbelong.keys():	

										if piname != groupbelong[researchname]:
											print(researchname+' duplicate!(in different group).Please correct it because the username should be unique')
											print(piname+' vs '+groupbelong[researchname])
											exit()
									else:
										groupbelong[researchname] = piname
								if fiscalname not in ['NA','N/A'] and fiscalname:
									if fiscalname in groupbelong.keys():
										if piname != groupbelong[fiscalname]:
											print(fiscalname+' duplicate!(in different group).Please correct it because the username should be unique')
											print(piname+' vs '+groupbelong[fiscalname])
											exit()
									else:
										groupbelong[fiscalname] = piname		

								group_name = '_'.join([x for x in piname.split(' ')])+'_group'
								#print(group_name)
								#objgroup, created = Group.objects.get_or_create(name=group_name)		

								nameparse = parsename(piname)
								if nameparse:
									passwordrand = ''.join(secrets.choice(alphabet) for i in range(10))
									
								else:
									print('PI name:'+piname+' can not parse!')	
			

								nameparse = parsename(researchname)
								if nameparse:
									passwordrand = ''.join(secrets.choice(alphabet) for i in range(10))
								else:
									print('Research name:'+researchname+' can not parse!')	
			

								nameparse = parsename(fiscalname)
								if nameparse:
									passwordrand = ''.join(secrets.choice(alphabet) for i in range(10))
								else:
									print('Fiscal name:'+fiscalname+' can not parse!')
								assignedsamp.append(sampindex)

	writeline = []
	groupbelong = {}
	assignedsamp = []
	sampfiles = ['scripts/MSTS.tsv','scripts/MSTS_Active.tsv']
	for file in sampfiles:
		with open(file,'r') as f:
			next(f)
			next(f)
			next(f)
			for line in f:
				fields = line.split('\t')
				if fields[0] and fields[1] and fields[1]!='N/A':
					sampindex = fields[21].strip()
					if not sampindex in assignedsamp:
						if not SampleInfo.objects.filter(sample_index=sampindex).exists():
							print(sampindex+' not stored in database!')
						else:
							if SampleInfo.objects.filter(sample_index=sampindex).count()>1:
								print(sampindex+' duplicate in database!')
							else:
								sampinfo = SampleInfo.objects.get(sample_index=sampindex)
								piname = fields[1].strip()
								researchname = fields[2].strip()
								fiscalname = fields[5].strip()	

								group_name = '_'.join([x for x in piname.split(' ')])+'_group'
								#print(group_name)
								objgroup, created = Group.objects.get_or_create(name=group_name)		

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
										writeline.append('\t'.join([objgroup.name,'PI',nameparse[0],passwordrand,nameparse[1],nameparse[2]]))
			

								nameparse = parsename(researchname)
								if nameparse:
									if researchname and researchname not in ['NA','N/A']:
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
												cell_phone = fields[4].strip(),
												role = 'Research'
												)
											writeline.append('\t'.join([objgroup.name,'Research',nameparse[0],passwordrand,nameparse[1],nameparse[2]]))										
										else:
											researchperson = CollaboratorPersonInfo.objects.get(person_id=User.objects.get(username=nameparse[0]))
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
												fiscal_index = fields[7].strip(),
												role = 'Fiscal'
												)
											writeline.append('\t'.join([objgroup.name,'Fiscal',nameparse[0],passwordrand,nameparse[1],nameparse[2]]))										
										else:
											fiscalperson=CollaboratorPersonInfo.objects.get(person_id=User.objects.get(username=nameparse[0]))
										sampinfo.fiscal_person = fiscalperson

								sampinfo.save()
								assignedsamp.append(sampindex)

	with open('scripts/collaboratorpassword.tsv','w') as fw:
		fw.write('\t'.join(['group','role','username','password','firstname','lastname']))
		fw.write('\n')
		fw.write('\n'.join(writeline))
		fw.write('\n')


if __name__ == '__main__':
	main()
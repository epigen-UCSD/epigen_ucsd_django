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

from masterseq_app.models import SampleInfo,LibraryInfo,SeqInfo,SeqMachineInfo,SeqBioInfo,GenomeInfo,ProtocalInfo
from nextseq_app.models import Barcode
from django.contrib.auth.models import User

def datetransform(inputdate):
	#from 2/6/2018 to 2018-02-06
	if inputdate == '':
		return ''
	tm = inputdate.split('/')
	year = tm[2].strip()
	month = tm[0].strip().zfill(2)
	date = tm[1].strip().zfill(2)
	if len(year) == 2:
		year = '20'+year
	return '-'.join([year,month,date])

def main():
	print("beginning")

# import GenomeInfo
	print("importing  GenomeInfo ........... ")
	species_genome = [
	'human_hg19',
	'human_hg38',
	'mouse_mm10',
	'rat_rn6',
	]
	for x in species_genome:
		obj,created = GenomeInfo.objects.get_or_create(
			species = x.split('_')[0],
			genome_name = x.split('_')[1],
		)

# import ProtocalInfo
	print("importing  ProtocalInfo ........... ")
	exptype = [
	'4C',
	'ATAC-seq',
	'CUT&RUN',
	'ChIP-seq',
	'Hi-C',
	'scATAC-seq',
	'scRNA-seq',
	'snRNA-seq',
	'Other (please explain in notes)',
	]
	for x in exptype:
		obj,created =ProtocalInfo.objects.get_or_create(
			experiment_type = x,
			protocal_name = 'Other (please explain in notes)',
			)

# import SeqMachineInfo
	print("importing  SeqMachineInfo ........... ")
	core_machine = [
	'EPIGEN_NextSeq550 High',
	'EPIGEN_NextSeq550 Mid',
	'IGM_HiSeq4000',
	'IGM_HiSeq4001',
	'IGM_HiSeq4002',
	'IGM_HiSeq4003',
	'IGM_HiSeq4004',
	'IGM_HiSeq4005',
	'IGM_HiSeq4006',
	'IGM_HiSeq4007',
	'IGM_HiSeq4008',
	'IGM_HiSeq4009',
	'IGM_HiSeq4010',
	'IGM_HiSeq4011',
	'IGM_HiSeq4012',
	'LICR_HiSeq4000',
	'LICR_HiSeq2500',
	'LICR_HiSeq4000',
	'LICR_Other',
	'Other_Other',
	]
	for x in core_machine:
		coreinfo = x.split('_')[0]
		machineinfo = x.split('_')[1]
		obj,created = SeqMachineInfo.objects.get_or_create(
			sequencing_core = coreinfo,
			machine_name = machineinfo,
			)

# import SampleInfo
	print("importing  SampleInfo ........... ")
	active_index = []
	active_index_2 = []
	with open('scripts/MSTS_Active.tsv','r') as f:
		next(f)
		next(f)
		next(f)
		for line in f:
			fields = line.split('\t')
			if fields[8]:
				if fields[12].split('(')[0].strip() == 'FACS sorted cells' or fields[12].split('(')[0].strip() == 'douncing homogenization':
					preparation_tm = 'other'
					note_tm = ';'.join([fields[28].strip(),fields[12].split('(')[0].strip()]).strip(';')

				elif fields[12].split('(')[0].strip() == 'flash frozen':
					preparation_tm = 'flash frozen without cryopreservant'
					note_tm = fields[28].strip()
				else:
					preparation_tm = fields[12].split('(')[0].strip()
					note_tm = fields[28].strip()
				active_index.append(fields[21].strip())
				active_index_2.append(fields[21].strip())

				obj,created = SampleInfo.objects.get_or_create(
					sample_id = fields[8].strip(),
					sample_index = fields[21].strip(),
					species = fields[10].split('(')[0].lower().strip(),
					sample_type = fields[11].split('(')[0].strip(),
					preparation = preparation_tm,
					description = fields[9].strip(),
					notes = note_tm,
				)

	with open('scripts/MSTS.tsv','r') as f:
		next(f)
		next(f)
		next(f)
		for line in f:
			fields = line.split('\t')
			if fields[8] and not fields[21].strip() in active_index:
				active_index_2.append(fields[21].strip())
				if fields[12].split('(')[0].strip() == 'FACS sorted cells' or fields[12].split('(')[0].strip() == 'douncing homogenization':
					preparation_tm = 'other'
					note_tm = ';'.join([fields[28].strip(),fields[12].split('(')[0].strip()]).strip(';')

				elif fields[12].split('(')[0].strip() == 'flash frozen':
					preparation_tm = 'flash frozen without cryopreservant'
					note_tm = fields[28].strip()
				else:
					preparation_tm = fields[12].split('(')[0].strip()
					note_tm = fields[28].strip()

				obj,created = SampleInfo.objects.get_or_create(
					sample_id = fields[8].strip(),
					sample_index = fields[21].strip(),
					species = fields[10].split('(')[0].lower().strip(),
					sample_type = fields[11].split('(')[0].strip(),
					preparation = preparation_tm,
					description = fields[9].strip(),
					notes = note_tm,
				)
	print('total sampleinfo in tracking sheet 1 is : '+str(SampleInfo.objects.count()))

# prepare for importing LibraryInfo
	libindexlist = []
	libnote_tm = {}
	libmemberini = {}
	libexperimenttype = {}
	libreferencetonotebook = {}
	libdate_started = {}
	libdate_completed = {}
	i = 1

	with open('scripts/METS_Active.tsv','r') as f:
		next(f)
		next(f)
		next(f)	
		for line in f:
			fields = line.split('\t')
			if fields[0].strip():
				libindexlist.append(fields[12].strip())
				libnote_tm[fields[12].strip()] = ';'.join([fields[11].strip(),fields[1].strip()]).strip(';')
				libmemberini[fields[12].strip()] = fields[2].strip()
				libexperimenttype[fields[12].strip()] = fields[5].strip()
				libreferencetonotebook[fields[12].strip()] = fields[7].strip()
				libdate_started[fields[12].strip()] = datetransform(fields[3].strip())
				libdate_completed[fields[12].strip()] = datetransform(fields[4].strip())


	with open('scripts/METS.tsv','r') as f:
		next(f)
		next(f)
		next(f)
		for line in f:
			fields = line.split('\t')
			if fields[0].strip() and not fields[12].strip() in libindexlist:
				libindexlist.append(fields[12].strip())
				libnote_tm[fields[12].strip()] = ';'.join([fields[11].strip(),fields[1].strip()]).strip(';')
				libmemberini[fields[12].strip()] = fields[2].strip()
				libexperimenttype[fields[12].strip()] = fields[5].strip()
				libreferencetonotebook[fields[12].strip()] = fields[7].strip()
				libdate_started[fields[12].strip()] = datetransform(fields[3].strip())
				libdate_completed[fields[12].strip()] = datetransform(fields[4].strip())
				

	#print(date_started)
	# for item in libdate_started:
	# 	print(libdate_started[item])
	# 	if isinstance(libdate_started[item],datetime.date):
	# 		print(item+': '+libdate_started[item])

# import LibraryInfo and SeqInfo
	print("importing LibraryInfo and SeqInfo ........... ")
	i = 1
	j = 1
	mseqtsfile = ['scripts/MSeqTS_Active.tsv','scripts/MSeqTS.tsv']
	#mseqtsfile = ['scripts/MSeqTS_merged.tsv']
	#mseqtsfile = ['scripts/MSeqTS.tsv']
	for files in mseqtsfile:
		print('from file: '+ files)
		with open(files,'r') as f:
			next(f)
			next(f)
			next(f)
			for line in f:
				fields = line.split('\t')
				if fields[0].strip():
					sequecingid = fields[8].strip()
					libraryid = fields[7].strip()
					if not SeqInfo.objects.filter(seq_id = sequecingid).exists():	
						experimentindex = fields[4].strip()
						
						if SampleInfo.objects.filter(sample_index = fields[0].strip()).exists():
							sample = SampleInfo.objects.get(sample_index = fields[0].strip())
						else:
							try:
								sample = SampleInfo.objects.get(sample_id = fields[1].strip(),species = fields[3].strip().lower())							
							except:
								if not LibraryInfo.objects.filter(library_id = libraryid).exists():
									
									sampleindex = 'SAMPNA-'+str(i)
									#print('newsample created:'+sampleindex+' with id:' +fields[1].strip())
									sample,created = SampleInfo.objects.get_or_create(
										sample_id = fields[1].strip(),
										sample_index = sampleindex,
										species = fields[3].strip().lower(),
										)
									i += 1
									if fields[0].startswith('SAMP') and experimentindex in libindexlist:
										#print(line)
										libnote_tm[experimentindex] = ';'.join([libnote_tm[experimentindex],fields[0].strip()]).strip(';')
										#print(fields[0].strip())
										#print(libnote_tm[experimentindex])
						if not LibraryInfo.objects.filter(library_id = libraryid).exists():
							if not fields[4].strip().startswith('EXP-'):
								experimentindex = 'EXPNA-'+str(j)
								j += 1
								#libraryid = fields[7].strip()
								experimenttype = fields[9].strip()
								libnotes = fields[17].strip()
								#print(libnotes)
								library,created = LibraryInfo.objects.get_or_create(
									experiment_index = experimentindex,
									sampleinfo = sample,
									library_id = libraryid,
									experiment_type = experimenttype,
									notes = libnotes,
									)	
						
							else:
								experimentindex = fields[4].strip()
								#libraryid = fields[7].strip()
								#print(experimentindex)
								try:
									protocal = ProtocalInfo.objects.get(experiment_type=libexperimenttype[experimentindex])
								except:
									protocal = None
									#print(fields[9].strip())
								if not experimentindex in libindexlist:
									print(experimentindex)
								if User.objects.filter(username = libmemberini[experimentindex]).exists():
									teammemberinitails = User.objects.get(username = libmemberini[experimentindex])				
								else:
									teammemberinitails = None
									if libmemberini[experimentindex]:
										libnote_tm[experimentindex] = ';'.join([libnote_tm[experimentindex],'team_member_initails:'+libmemberini[experimentindex]]).strip(';')				
								if libdate_started[experimentindex]:
									datestarted = libdate_started[experimentindex]
								else:
									datestarted = None				
								if libdate_completed[experimentindex]:
									datecompleted = libdate_completed[experimentindex]
								else:
									datecompleted = None				
								library,created = LibraryInfo.objects.get_or_create(
									experiment_index = experimentindex,
									sampleinfo = sample,
									library_id = libraryid,
									experiment_type = libexperimenttype[experimentindex],
									reference_to_notebook_and_page_number = libreferencetonotebook[experimentindex],
									date_started = datestarted,
									date_completed = datecompleted,
									team_member_initails = teammemberinitails,
									protocalinfo = protocal,
									notes = libnote_tm[experimentindex],
									)
						else:
							library = LibraryInfo.objects.get(library_id = libraryid)	
			
		
						note_tm = fields[17].strip()
						try:
							portionoflane = float(fields[14].strip())
						except:
							portionoflane = None
							if not fields[14].strip() in ['N/A','NA']:
								note_tm = ';'.join([note_tm,'portionoflane:'+fields[14].strip()]).strip(';')			
						try:
							totalreadsnum = int(fields[22].strip().replace(',', ''))
						except:
							totalreadsnum = None
							if fields[22].strip() != 'NA':
								note_tm = ';'.join([note_tm,'totalreadsnum:'+fields[22].strip()]).strip(';')
						try:
							teammemberinitails = User.objects.get(username = fields[5].strip())
						except:
							teammemberinitails = None
						if SeqMachineInfo.objects.filter(sequencing_core = fields[10].split('(')[0].strip(),machine_name = fields[11].split('(')[0].strip()).exists():
							machineused = SeqMachineInfo.objects.get(sequencing_core = fields[10].split('(')[0].strip(),machine_name = fields[11].split('(')[0].strip())
						elif not fields[10].strip() and not fields[11].strip():
							machineused = None
						else:
							note_tm = ';'.join([note_tm,'sequencingmachine:'+fields[10].strip()+'_'+fields[11].strip()]).strip(';')
							machineused = None
							#print( fields[10].strip()+'\t'+fields[11].strip())
						try:
							teammemberinitails = User.objects.get(username = fields[5].strip())
						except:
							teammemberinitails = None
							if fields[5].strip() and fields[5].strip()!= 'Other (please explain in notes)':						
								note_tm = ';'.join([note_tm,'team_member_initails:'+fields[5].strip()]).strip(';')
						try:
							i7index_tm = Barcode.objects.get(indexid=fields[15].strip())
						except:
							i7index_tm = None
							if  fields[15].strip() and not fields[15].strip() in ['NA','Other (please explain in notes)','N/A']:
								note_tm = ';'.join([note_tm,'i7index:'+fields[15].strip()]).strip(';')
								#print(fields[15].strip())
						try:
							i5index_tm = Barcode.objects.get(indexid=fields[16].strip())
						except:
							i5index_tm = None
							if  fields[16].strip() and not fields[16].strip() in ['NA','Other (please explain in notes)','N/A']:
								note_tm = ';'.join([note_tm,'i5index:'+fields[16].strip()]).strip(';')
								#print(fields[16].strip())
						if fields[6].strip() in ['N/A','NA','']:
							datesub = None
						elif '-' in fields[6].strip():
							datesub = fields[6].strip()
						else:
							datesub = datetransform(fields[6].strip())			
						# if not fields[13].strip() in ['PE','SE']:
						# 	print(fields[13].strip())		

						sequencing,created = SeqInfo.objects.get_or_create(
							seq_id = sequecingid,
							libraryinfo = library,
							team_member_initails = teammemberinitails,
							read_length = fields[12].strip(),
							read_type = fields[13].strip(),
							portion_of_lane = portionoflane,
							total_reads = totalreadsnum,
							notes = note_tm,
							machine = machineused,
							i7index = i7index_tm,
							i5index = i5index_tm,
							date_submitted_for_sequencing = datesub,
							)
					genomeinfo = fields[21].strip()
					if genomeinfo and genomeinfo != 'NA':
						genomeinfothis = GenomeInfo.objects.get( genome_name=genomeinfo )
						pipelineversion = ''
						finalreads = int(fields[23].strip().replace(',', ''))
						finalyield = float(fields[24].strip())
						mitofrac = float(fields[25].strip())
						tssenrichment = float(fields[26].strip())
						fropthis = float(fields[27].strip())
						obj,created = SeqBioInfo.objects.get_or_create(
							seqinfo = SeqInfo.objects.get(seq_id = sequecingid),
							genome = genomeinfothis,
							pipeline_version = pipelineversion,
							final_reads = finalreads,
							final_yield = finalyield,
							mito_frac = mitofrac,
							tss_enrichment = tssenrichment,
							frop = fropthis,
							)

	print('total sampleinfo is : '+str(SampleInfo.objects.count()))
	print('total librayinfo is : '+str(LibraryInfo.objects.count()))
	print('total seqinfo is : '+str(SeqInfo.objects.count()))
	print('total seqbioinfo is : '+str(SeqBioInfo.objects.count()))

				


if __name__ == '__main__':
	main()
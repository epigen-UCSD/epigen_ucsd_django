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

def main():
	print("beginning")
	#alllibs=[]

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
	'other (please explain in notes)',
	]
	for x in exptype:
		obj,created =ProtocalInfo.objects.get_or_create(
			experiment_type = x,
			protocal_name = 'other (please explain in notes)',
			)

# import SeqMachineInfo
	print("importing  SeqMachineInfo ........... ")
	core_machine = [
	'EPIGEN_NextSeq550 High',
	'EPIGEN_NextSeq550 Mid',
	'IGM_HiSeq4000',
	'LICR_HiSeq4000',
	'LICR_HiSeq2500',
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
	print("importing SampleInfo ........... ")
	active_index = []
	notimporting_samp =[]
	with open('scripts/TS1_Active.tsv','r') as f:
		next(f)
		next(f)
		next(f)
		for line in f:
			fields = line.split('\t')
			if fields[8]:
				#print(fields[21].strip())
				active_index.append(fields[21].strip())
				sampletype_tm = fields[11].strip().lower()
				species_tm = fields[10].lower().strip()
				preparation_tm = fields[12].lower().strip()
				fixation_tm = fields[13].strip()
				notes_tm = ';'.join([fields[20].strip(),fields[28].strip()]).strip(';')
				unit_tm = fields[15].lower().strip()
				service_requested_tm = fields[16].strip()
				seq_depth_to_target_tm = fields[17].strip()
				seq_length_requested_tm = fields[18].strip()
				seq_type_requested_tm = fields[19].strip()
				storage_tm = fields[26].strip()

				if sampletype_tm == 'pca cell line':
					notes_tm = ';'.join([notes_tm,sampletype_tm]).strip(';')
					sampletype_tm = 'other (please explain in notes)'
				elif sampletype_tm.startswith('other'):
					sampletype_tm = 'other (please explain in notes)'

				if User.objects.filter(username = fields[25].strip()).exists():
					team_member_tm = User.objects.get(username = fields[25].strip())				
				else:
					team_member_tm = None
					if fields[25].strip()!='':
						notes_tm = ';'.join([notes_tm,'team_member_initails:'+fields[25].strip()]).strip(';')

				if species_tm.startswith('other'):
					species_tm = 'other (please explain in notes)'

				if preparation_tm in ['facs sorted cells','douncing homogenization']:
					notes_tm = ';'.join([notes_tm,'sample preparation:',preparation_tm]).strip(';')
					preparation_tm = 'other (please explain in notes)'
				elif preparation_tm.startswith('other'):
					preparation_tm = 'other (please explain in notes)'

				if fixation_tm.lower().startswith('other'):
					fixation_tm = 'other (please explain in notes)'

				if unit_tm.startswith('other'):
					unit_tm = 'other (please explain in notes)'

				if service_requested_tm.lower().startswith('other'):
					service_requested_tm = 'other (please explain in notes)'

				obj,created = SampleInfo.objects.get_or_create(
					sample_index = fields[21].strip(),
				)
				if obj.sample_id:
					if obj.sample_id != fields[8].strip():
						print("Inconsistent with last importing: "+sample_index+';'+fields[8].strip()+';'+obj.sample_id)
				obj.sample_id = fields[8].strip()
				obj.date =  datetransform(fields[0].strip())
				obj.team_member = team_member_tm
				obj.species = species_tm
				obj.sample_type = sampletype_tm
				obj.preparation = preparation_tm
				obj.description = fields[9].strip()
				obj.fixation = fixation_tm
				obj.notes = notes_tm
				obj.sample_amount = fields[14].strip()
				obj.unit = unit_tm
				obj.service_requested = service_requested_tm
				obj.seq_depth_to_target = seq_depth_to_target_tm
				obj.seq_length_requested = seq_length_requested_tm
				obj.seq_type_requested = seq_type_requested_tm
				obj.storage = storage_tm
				obj.date_received = datetransform(fields[23].strip())
				obj.save()
			else:
				#print(line.strip('\n'))
				notimporting_samp.append(line.strip('\n'))

	with open('scripts/TS1_Archived.tsv','r') as f:
		next(f)
		next(f)
		next(f)
		for line in f:
			fields = line.split('\t')
			if fields[8] and not fields[21].strip() in active_index:
				#print(fields[21].strip())
				sampletype_tm = fields[11].strip().lower()
				species_tm = fields[10].lower().strip()
				preparation_tm = fields[12].lower().strip()
				fixation_tm = fields[13].strip()
				notes_tm = ';'.join([fields[20].strip(),fields[28].strip()]).strip(';')
				unit_tm = fields[15].lower().strip()
				service_requested_tm = fields[16].strip()
				seq_depth_to_target_tm = fields[17].strip()
				seq_length_requested_tm = fields[18].strip()
				seq_type_requested_tm = fields[19].strip()
				storage_tm = fields[26].strip()

				if sampletype_tm == 'pca cell line':
					notes_tm = ';'.join([notes_tm,sampletype_tm]).strip(';')
					sampletype_tm = 'other (please explain in notes)'
				elif sampletype_tm.startswith('other'):
					sampletype_tm = 'other (please explain in notes)'

				if User.objects.filter(username = fields[25].strip()).exists():
					team_member_tm = User.objects.get(username = fields[25].strip())				
				else:
					team_member_tm = None
					if fields[25].strip()!='':
						notes_tm = ';'.join([notes_tm,'team_member_initails:'+fields[25].strip()]).strip(';')

				if species_tm.startswith('other'):
					species_tm = 'other (please explain in notes)'

				if preparation_tm in ['facs sorted cells','douncing homogenization']:
					notes_tm = ';'.join([notes_tm,'sample preparation:',preparation_tm]).strip(';')
					preparation_tm = 'other (please explain in notes)'
				elif preparation_tm.startswith('other'):
					preparation_tm = 'other (please explain in notes)'

				if fixation_tm.startswith('other'):
					fixation_tm = 'other (please explain in notes)'

				if unit_tm.startswith('other'):
					unit_tm = 'other (please explain in notes)'

				if service_requested_tm.lower().startswith('other'):
					service_requested_tm = 'other (please explain in notes)'

				obj,created = SampleInfo.objects.get_or_create(
					sample_index = fields[21].strip(),
				)
				if obj.sample_id:
					if obj.sample_id != fields[8].strip():
						print("Inconsistent with last importing: "+sample_index+';'+fields[8].strip()+';'+obj.sample_id)
				obj.sample_id = fields[8].strip()
				obj.date =  datetransform(fields[0].strip())
				obj.team_member = team_member_tm
				obj.species = species_tm
				obj.sample_type = sampletype_tm
				obj.preparation = preparation_tm
				obj.description = fields[9].strip()
				obj.fixation = fixation_tm
				obj.notes = notes_tm
				obj.sample_amount = fields[14].strip()
				obj.unit = unit_tm
				obj.service_requested = service_requested_tm
				obj.seq_depth_to_target = seq_depth_to_target_tm
				obj.seq_length_requested = seq_length_requested_tm
				obj.seq_type_requested = seq_type_requested_tm
				obj.storage = storage_tm
				obj.date_received = datetransform(fields[23].strip())
				obj.save()
			else:
				#print(line.strip('\n'))
				notimporting_samp.append(line.strip('\n'))
	print('total sampleinfo in tracking sheet 1 is : '+str(SampleInfo.objects.count()))



# import Libinfo
	print("importing LibraryInfo ........... ")
	libidall = []
	libindexlist = []
	notimporting_lib =[]
	i = 1
	k = 1
	with open('scripts/TS2_Active.tsv','r') as f:
		next(f)
		next(f)
		next(f)	
		for line in f:
			fields = line.split('\t')
			if not fields[10].strip() in ['','NA']:
				libid = '_'.join(fields[10].strip().split('-'))
				if libid in libidall:
					print('library id duplicate:'+libid)
				libidall.append(libid)
				libindexlist.append(fields[12].strip())
				libnote_tm = fields[11].strip()
				libnote_tm = ';'.join([libnote_tm,'Protocol used(recorded in Tracking Sheet 2):'+fields[6].strip()]).strip(';')
				libexp_tm = fields[5].strip()
				libreferencetonotebook_tm = fields[7].strip()
				if libexp_tm in ['Hi-C Arima Kit','Hi-C Epigen']:
					libnote_tm = ';'.join([libnote_tm,libexp_tm]).strip(';')
					libexp_tm = 'Hi-C'
				if libexp_tm.lower().startswith('other'):
					libexp_tm = 'other (please explain in notes)'
				libreferencetonotebook = fields[7].strip()
				if User.objects.filter(username = fields[2].strip()).exists():
					lib_member_tm = User.objects.get(username = fields[2].strip())
				else:
					lib_member_tm = None
					if fields[2].strip()!='':					
						libnote_tm = ';'.join([libnote_tm,'team_member_initails:'+fields[2].strip()]).strip(';')
				if not fields[0].strip().lower() in ['','na','other','n/a','samp-388 / samp-389','samp-344 & 345','samp-352 & 353']:
					try:
						sampinfo = SampleInfo.objects.get(sample_index = fields[0].strip())
					except:
						print(line)
				else:
					if fields[0].strip().lower() in ['samp-388 / samp-389','samp-344 & 345','samp-352 & 353']:
						sampindextm = fields[0].strip()
						samp_notes = fields[0].strip()
					else:
						sampindextm = 'SAMPNA-'+str(i)
						samp_notes = ''
						i = i+1
					if fields[1].strip():
						sampidtm = fields[1].strip()
					else:
						sampidtm = sampindextm
					sampinfo,created = SampleInfo.objects.get_or_create(sample_index=sampindextm)
					sampinfo.sample_id = sampidtm
					sampinfo.species = ''
					sampinfo.team_member = lib_member_tm
					try:
						sampinfo.notes = samp_notes
					except:
						pass
					sampinfo.save()
				
				obj,created = LibraryInfo.objects.get_or_create(
					library_id = libid,
				)
				obj.experiment_index = fields[12].strip()
				obj.experiment_type = libexp_tm
				if libexp_tm!='':
					obj.protocalinfo = ProtocalInfo.objects.get(experiment_type = libexp_tm,protocal_name = 'other (please explain in notes)',)
				else:
					obj.protocalinfo = ProtocalInfo.objects.get(experiment_type = 'other (please explain in notes)',protocal_name = 'other (please explain in notes)',)
				obj.reference_to_notebook_and_page_number = libreferencetonotebook
				obj.date_started = datetransform(fields[3].strip())
				obj.date_completed = datetransform(fields[4].strip())
				obj.team_member_initails = lib_member_tm
				obj.notes = libnote_tm
				obj.sampleinfo = sampinfo
				obj.save()
			else:
				#print(line.strip('\n'))
				notimporting_lib.append(line.strip('\n'))


	with open('scripts/TS2_Archived.tsv','r') as f:
		next(f)
		next(f)
		next(f)
		for line in f:
			fields = line.split('\t')
			#if not fields[12].strip() in libindexlist:
			if not fields[10].strip() in libidall:
				if not fields[10].strip() in ['','NA']:
					libid = '_'.join(fields[10].strip().split('-'))
					if libid in libidall:
						print('library id duplicate:'+libid)
					libidall.append(libid)
					libindexlist.append(fields[12].strip())
					libnote_tm = fields[11].strip()
					libnote_tm = ';'.join([libnote_tm,'Protocol used(recorded in Tracking Sheet 2):'+fields[6].strip()]).strip(';')
					if libid.startswith('XH_71['):
						libnote_tm = ';'.join([libnote_tm,'From sample '+fields[1].strip()]).strip(';')
					libexp_tm = fields[5].strip()
					libreferencetonotebook_tm = fields[7].strip()
					if libexp_tm in ['Hi-C Arima Kit','Hi-C Epigen']:
						libnote_tm = ';'.join([libnote_tm,libexp_tm]).strip(';')
						libexp_tm = 'Hi-C'
					if libexp_tm.lower().startswith('other'):
						libexp_tm = 'other (please explain in notes)'
					libreferencetonotebook = fields[7].strip()
					if User.objects.filter(username = fields[2].strip()).exists():
						lib_member_tm = User.objects.get(username = fields[2].strip())
					else:
						lib_member_tm = None
						if fields[2].strip()!='':					
							libnote_tm = ';'.join([libnote_tm,'team_member_initails:'+fields[2].strip()]).strip(';')
					if not fields[0].strip().lower() in ['','na','other','n/a','samp-388 / samp-389','samp-344 & 345','samp-352 & 353']:
						try:
							sampinfo = SampleInfo.objects.get(sample_index = fields[0].strip())
						except:
							print(line)
					else:
						notestmtm = ''
						if fields[0].strip().lower() in ['samp-388 / samp-389','samp-344 & 345','samp-352 & 353']:
							sampindextm = fields[0].strip()
							samp_notes = fields[0].strip()
						else:
							sampindextm = 'SAMPNA-'+str(i)
							samp_notes = ''
							i = i+1
						if fields[1].strip():
							sampidtm = fields[1].strip()
						else:
							sampidtm = sampindextm
						sampinfo,created = SampleInfo.objects.get_or_create(sample_index=sampindextm)
						sampinfo.sample_id = sampidtm
						sampinfo.species = ''
						sampinfo.team_member = lib_member_tm
						try:
							sampinfo.notes = samp_notes
						except:
							pass
						sampinfo.save()			
					obj,created = LibraryInfo.objects.get_or_create(
						library_id = libid,
					)
					obj.experiment_index = fields[12].strip()
					obj.experiment_type = libexp_tm
					if libexp_tm!='':
						obj.protocalinfo = ProtocalInfo.objects.get(experiment_type = libexp_tm,protocal_name = 'other (please explain in notes)',)
					else:
						obj.protocalinfo = ProtocalInfo.objects.get(experiment_type = 'other (please explain in notes)',protocal_name = 'other (please explain in notes)',)
					obj.reference_to_notebook_and_page_number = libreferencetonotebook
					obj.date_started = datetransform(fields[3].strip())
					obj.date_completed = datetransform(fields[4].strip())
					obj.team_member_initails = lib_member_tm
					obj.notes = libnote_tm
					obj.sampleinfo = sampinfo
					obj.save()
					
				else:
					#print(line.strip('\n'))
					notimporting_lib.append(line.strip('\n'))



# importing SeqInfo
	print("importing SeqInfo ........... ")
	j = 1
	mseqtsfile = ['scripts/TS3_Active.tsv','scripts/TS3_Archived.tsv']
	sequecingidall = []
	notimporting_seq = []
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
				if fields[8].strip():
					sequecingid = fields[8].strip()
					libraryid = fields[7].strip()
					sampspecies = fields[3].lower().strip()
					note_tm = fields[17].strip()
					try:
						teammemberinitails = User.objects.get(username = fields[5].strip())
					except:
						teammemberinitails = None
						if fields[5].strip()!='':					
							note_tm = ';'.join([note_tm,'team_member_initails:'+fields[5].strip()]).strip(';')

					
					#if not SeqInfo.objects.filter(seq_id = sequecingid).exists():
					if not sequecingid in sequecingidall:
						sequecingidall.append(sequecingid)
						experimentindex = fields[4].strip()
						#if not LibraryInfo.objects.filter(library_id = libraryid).exists():
						if not libraryid in libidall:
							print(libraryid)
							libidall.append(libraryid)
							experimentindex = 'EXPNA-'+str(j)
							j += 1
							experimenttype = fields[9].strip()
							if SampleInfo.objects.filter(sample_index = fields[0].strip()).exists():
								sample = SampleInfo.objects.get(sample_index = fields[0].strip())
							else:
								sampleindex = 'SAMPNA-'+str(i)
								i += 1
								if fields[1].strip():
									sampid_tm = fields[1].strip()
								else:
									sampid_tm = sampleindex

								
								sample,created = SampleInfo.objects.get_or_create(sample_index = sampleindex,)				
								sample.sample_id = 	sampid_tm	
								sample.species = fields[3].strip().lower()
								sample.team_member = teammemberinitails
								sample.save()
								
							library,created = LibraryInfo.objects.get_or_create(library_id = libraryid)									
							library.sampleinfo = sample
							library.experiment_index = experimentindex
							library.experiment_type = experimenttype
							library.team_member_initails = teammemberinitails
							library.save()
						
						else:
							#print(libraryid)
							library = LibraryInfo.objects.get(library_id = libraryid)
							sampinfo = library.sampleinfo
							if not sampinfo.species and sampspecies:
								sampinfo.species = sampspecies
								sampinfo.save()
						try:
							portionoflane = float(fields[14].strip())
						except:
							portionoflane = None
							if not fields[14].strip() in ['','NA', 'Other (please explain in notes)', 'N/A']:
								note_tm = ';'.join([note_tm,'portionoflane:'+fields[14].strip()]).strip(';')			
						try:
							totalreadsnum = int(fields[22].strip().replace(',', ''))
						except:
							totalreadsnum = None
							if not fields[22].strip() in ['','NA', 'Other (please explain in notes)', 'N/A']:
								note_tm = ';'.join([note_tm,'totalreadsnum:'+fields[22].strip()]).strip(';')
						if SeqMachineInfo.objects.filter(sequencing_core = fields[10].split('(')[0].strip(),machine_name = fields[11].split('(')[0].strip()).exists():
							machineused = SeqMachineInfo.objects.get(sequencing_core = fields[10].split('(')[0].strip(),machine_name = fields[11].split('(')[0].strip())
						elif not fields[10].strip() and not fields[11].strip():
							machineused = None
						else:
							note_tm = ';'.join([note_tm,'sequencingmachine:'+fields[10].strip()+'_'+fields[11].strip()]).strip(';')
							machineused = None
							#print( fields[10].strip()+'\t'+fields[11].strip())
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
						datesub = datetransform(fields[6].strip())
						readtype_tm = fields[13].strip()
						if readtype_tm.lower().startswith('other'):
							readtype_tm = 'other (please explain in notes)'
						# if not fields[13].strip() in ['PE','SE']:
						# 	print(fields[13].strip())
						sequencing,created = SeqInfo.objects.get_or_create(seq_id = sequecingid)			
						sequencing.libraryinfo = library
						sequencing.team_member_initails = teammemberinitails
						sequencing.read_length = fields[12].strip()
						sequencing.read_type = readtype_tm
						sequencing.portion_of_lane = portionoflane
						sequencing.total_reads = totalreadsnum
						sequencing.notes = note_tm
						sequencing.machine = machineused
						sequencing.i7index = i7index_tm
						sequencing.i5index = i5index_tm
						sequencing.default_label = fields[2].strip()
						sequencing.date_submitted_for_sequencing = datesub
						sequencing.save()

					genomeinfo = fields[21].strip()
					if genomeinfo and genomeinfo != 'NA':
						genomeinfothis = GenomeInfo.objects.get( genome_name=genomeinfo )
						pipelineversion = ''
						finalreads = int(fields[23].strip().replace(',', ''))
						finalyield = float(fields[24].strip())
						mitofrac = float(fields[25].strip())
						tssenrichment = float(fields[26].strip())
						fropthis = float(fields[27].strip())
						obj,created = SeqBioInfo.objects.get_or_create(seqinfo = SeqInfo.objects.get(seq_id = sequecingid),genome = genomeinfothis,)							
						obj.pipeline_version = pipelineversion
						obj.final_reads = finalreads
						obj.final_yield = finalyield
						obj.mito_frac = mitofrac
						obj.tss_enrichment = tssenrichment
						obj.frop = fropthis
						obj.save()
				else:
					#print(line.strip('\n'))
					notimporting_seq.append(line.strip('\n'))

	print('total sampleinfo is : '+str(SampleInfo.objects.count()))
	print('total librayinfo is : '+str(LibraryInfo.objects.count()))
	print('total seqinfo is : '+str(SeqInfo.objects.count()))
	print('total seqbioinfo is : '+str(SeqBioInfo.objects.count()))
	print(str(i))
	print(str(j))
	with open('scripts/notimporting.tsv','w') as fw:
		fw.write('libraries:\n')
		fw.write('\n'.join(notimporting_lib))
		fw.write('\n')
		fw.write('Sequencings:\n')
		fw.write('\n'.join(notimporting_seq))
		fw.write('\n')

				


if __name__ == '__main__':
	main()
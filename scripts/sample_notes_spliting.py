#!/usr/bin/env python
import os
import sys
import django

scriptpath = os.path.dirname(os.path.realpath(__file__))
os.chdir("../")
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()

from masterseq_app.models import SampleInfo


def main():
	file1 = os.path.join(scriptpath,'ts1_20190821_for_notes_spliting_active.tsv')
	file2 = os.path.join(scriptpath,'ts1_20190821_for_notes_spliting_archived.tsv')
	allsamples = []
	internal_notes_all = {}
	with open(file1,'r') as f:
		next(f)
		next(f)
		next(f)
		for line in f:
			fields = line.strip('\n').split('\t')
			if fields[21]:
				allsamples.append(fields[21].strip())
				internal_notes_all[fields[21].strip()] = fields[28].strip()


	with open(file2,'r') as f:
		next(f)
		next(f)
		next(f)
		for line in f:
			fields = line.strip('\n').split('\t')
			if fields[21]:
				if fields[21].strip() not in allsamples:
					internal_notes_all[fields[21].strip()] = fields[28].strip()

	for samp in internal_notes_all.keys():
		notes_final = []
		try:
			current_sam = SampleInfo.objects.get(sample_index=samp)
			#print(samp+':'+current_sam.sample_id)
			current_notes = current_sam.notes
			#print(current_notes)
			notes_field = current_notes.split(';')
			if internal_notes_all[samp]:
				for c in notes_field:				
					if internal_notes_all[samp] in c:
						current_sam.internal_notes = c
						#print(c)
					else:
						notes_final.append(c)
				current_sam.notes = ';'.join(notes_final)
				current_sam.save()

		except:
			pass
		

			
if __name__ == '__main__':
	main()
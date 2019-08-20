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

from masterseq_app.models import LibraryInfo


def main():
	for lib in LibraryInfo.objects.all():
		notes_final = []
		print(lib.library_id)
		if 'Protocol used(recorded in Tracking Sheet 2):;' in lib.notes:
			notes_tm = lib.notes.replace(':;',':')
		else:
			notes_tm = lib.notes
		notes_field = notes_tm.split(';')
		for c in notes_field:
			if 'Protocol used(recorded in Tracking Sheet 2):' not in c:
				notes_final.append(c)
			else:
				lib.protocal_used = c.split(':')[1]
		lib.notes = ';'.join(notes_final)
		lib.protocalinfo = None
		lib.save()

			
if __name__ == '__main__':
	main()
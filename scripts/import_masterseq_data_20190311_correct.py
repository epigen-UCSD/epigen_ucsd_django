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

from masterseq_app.models import SampleInfo,LibraryInfo,SeqInfo
from django.contrib.auth.models import User


def main():
	sampinfo1,created = SampleInfo.objects.get_or_create(sample_index='samp-388/samp-389[1]',sample_id='C4_2_Input',team_member=User.objects.get(username ='AVD'),species='human',notes='samp-388/samp-389')
	sampinfo2,created = SampleInfo.objects.get_or_create(sample_index='samp-388/samp-389[2]',sample_id='C4_2_H3K27me3',team_member=User.objects.get(username ='AVD'),species='human',notes='samp-388/samp-389')
	sampinfo3,created = SampleInfo.objects.get_or_create(sample_index='samp-388/samp-389[3]',sample_id='C4_2_H3K4me3_1',team_member=User.objects.get(username ='AVD'),species='human',notes='samp-388/samp-389')
	sampinfo4,created = SampleInfo.objects.get_or_create(sample_index='samp-388/samp-389[4]',sample_id='C4_2_H3K4me3_2',team_member=User.objects.get(username ='AVD'),species='human',notes='samp-388/samp-389')
	lib1=LibraryInfo.objects.get(library_id = 'AVD_108')
	lib1.sampleinfo=sampinfo2
	lib1.save()
	lib2=LibraryInfo.objects.get(library_id = 'AVD_109')
	lib2.sampleinfo=sampinfo3
	lib2.save()
	lib3=LibraryInfo.objects.get(library_id = 'AVD_110')
	lib3.sampleinfo=sampinfo4
	lib3.save()
	lib4=LibraryInfo.objects.get(library_id = 'AVD_111')
	lib4.sampleinfo=sampinfo1
	lib4.save()
	lib5=LibraryInfo.objects.get(library_id = 'AVD_83_2')
	lib5.sampleinfo=sampinfo2
	lib5.save()
	lib6=LibraryInfo.objects.get(library_id = 'AVD_84_2')
	lib6.sampleinfo=sampinfo3
	lib6.save()
	lib7=LibraryInfo.objects.get(library_id = 'AVD_84_3')
	lib7.sampleinfo=sampinfo4
	lib7.save()
	lib8=LibraryInfo.objects.get(library_id = 'AVD_85_2')
	lib8.sampleinfo=sampinfo1
	lib8.save()

	sampinfo5,created = SampleInfo.objects.get_or_create(sample_index='SAMP-344 & 345[1]',sample_id='A_#001 & B_#001_1',species='human',notes='SAMP-344 & 345')
	sampinfo6,created = SampleInfo.objects.get_or_create(sample_index='SAMP-344 & 345[2]',sample_id='A_#001 & B_#001_2',species='human',notes='SAMP-344 & 345')
	lib9=LibraryInfo.objects.get(library_id = 'XW23')
	lib9.sampleinfo=sampinfo5
	lib9.save()
	lib10=LibraryInfo.objects.get(library_id = 'XW24')
	lib10.sampleinfo=sampinfo6
	lib10.save()

	sampinfo7,created = SampleInfo.objects.get_or_create(sample_index='SAMP-352 & 353[1]',sample_id='A_#002 & B_#002_1',species='human',notes='SAMP-352 & 353')
	sampinfo8,created = SampleInfo.objects.get_or_create(sample_index='SAMP-352 & 353[2]',sample_id='A_#002 & B_#002_2',species='human',notes='SAMP-352 & 353')
	lib11=LibraryInfo.objects.get(library_id = 'XW25')
	lib11.sampleinfo=sampinfo7
	lib11.save()
	lib12=LibraryInfo.objects.get(library_id = 'XW26')
	lib12.sampleinfo=sampinfo8
	lib12.save()

	for ids in ['SAMP-388 / SAMP-389','SAMP-344 & 345','SAMP-352 & 353']:
		sampleinfo=SampleInfo.objects.get(sample_index=ids)
		sampleinfo.delete()
	for seqid in ['RMM_29','RMM_30','RMM_31','RMM_32','RMM_33','RMM_34','RMM_35']:
		seq_tm = SeqInfo.objects.get(seq_id=seqid)
		seq_tm.seq_id = '_'.join([seqid.split('_')[0],str(int(seqid.split('_')[1])-1)])
		seq_tm.save()

	sampleids = list(SampleInfo.objects.values_list('sample_id', flat=True))
	id_dict = {i:sampleids.count(i) for i in sampleids}
	#print(sampleids)
	print(id_dict)
	for item,counts in id_dict.items():
		queryset = SampleInfo.objects.filter(sample_id=item).order_by('date')
		# for query in queryset:
		# 	id_tm = query.sample_id
		# 	query.sample_id = id_tm.rsplit('[',1)[0]
		# 	query.save()
		if counts>1:
			i = 1
			for query in queryset:
				query.sample_id=item+'['+str(i)+']'
				query.save()
				i += 1

if __name__ == '__main__':
	main()

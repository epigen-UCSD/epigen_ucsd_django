#!/usr/bin/env python
import argparse
import subprocess
import requests
import json
import datetime
import time
import re
import django
from django.contrib.auth.models import Group,User

os.chdir("../")
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()
from masterseq_app.models import SampleInfo,LibraryInfo,SeqInfo


def main():
    # python encode_step1_grab_metadata_from_link.py -u liyuxin -l "https://www.encodeproject.org/search/?type=Experiment&status=released&assay_title=Histone+ChIP-seq&biosample_ontology.term_name=K562&target.label=H3K4me3&target.label=H3K36me3&target.label=H3K27me3&target.label=H3K27ac&target.label=H3K4me1"
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', help='link from encode')
    parser.add_argument('-u',help = 'the user(username) who requests this ENCODE setqc')

    cell_labels = ['cell line', 'primary cell', 'in vitro differentiated cells']
    tissue_labels = ['tissue']

    url = parser.parse_args().l
    headers = {'accept': 'application/json'}
    response = requests.get(url, headers=headers)
    biosample = response.json()
    graph = biosample['@graph']

    # First, biosamples.... ================================

    start = time.time()
    biosample_list = []
    tosave_list = []
    for x in graph:
        for y in x['replicates']:
            biosample_list.append(str(y['library']['biosample']['accession']))
    print(set(biosample_list))
    for sample in set(biosample_list):
        this_url = "https://www.encodeproject.org/"+sample+"/?frame=embedded"
        response = requests.get(this_url, headers=headers)
        this_sample = response.json()
        if str(this_sample['biosample_ontology']['classification']) in cell_labels:
            this_sample_type = 'cultured cells'
        elif str(this_sample['biosample_ontology']['classification']) in tissue_labels:
            this_sample_type = 'tissue'
        else:
            this_sample_type = 'other (please explain in notes)'
        today = datetime.date.today()
        sample_id=str(this_sample['biosample_ontology']['term_name'])+'_'+sample

        sample_type=this_sample_type
        date=today

        if not SampleInfo.objects.filter(sample_id=sample_id).exists():
            tosave_item = SampleInfo(
                sample_id=sample_id,
                description=str(this_sample['summary']),
                species=str(this_sample['organism']['name']),
                sample_type=this_sample_type,
                date=today,
                group=Group.objects.get(name='David Gorkin'),
                notes='pseudosample, data downloaded from ENCODE',
                )   
            tosave_list.append(tosave_item)
    SampleInfo.objects.bulk_create(tosave_list)
    end = time.time()
    print(end - start)

    # Next, libraries.... ================================
    start = time.time()
    library_list = []
    library_id_list = []
    lib_sam = {}
    tosave_list = []
    ib_new_name = []
    for x in graph:
        for y in x['replicates']:
            library_list.append(str(y['@id']))
    print(set(library_list))
    for library in set(library_list):
        this_url = "https://www.encodeproject.org/"+library+"/?frame=embedded"
        response = requests.get(this_url, headers=headers)
        this_library = response.json()

        this_id=str(this_library['libraries'][0]['accession'])
        notes=';'.join(['pseudolibrary, ENCODE library downloaded from encodeproject.org','ENCODE accession:'+this_id])

        library_id_list.append(this_id)
        lib_sam[this_id] = sampleinfo
        existing_flag = 0
        thissample = SampleInfo.objects,get(sample_id=str(this_library['library']['biosample']['accession']))
        for item in thissample.libraryinfo_set.all():
            if this_id == item.notes.split(';')[1].split(':')[1]:
                lib_new_name[this_id] = item.library_id
                existing_flag = 1
                break;
            else:
                existing_flag = 0
        lib_ids = list(LibraryInfo.objects.values_list('library_id', flat=True))
        maxid = max([int(x.split('_')[1]) for x in lib_ids if x.startswith('ENCODE')])
        libid_new = '_'.join(['ENCODE', str(maxid+1)])
        lib_new_name[libid] = libid_new
        if existing_flag == 0:
            tosave_item = LibraryInfo(
                sampleinfo=thissample,
                library_description=' '.join(['ENCODE',str(this_library['experiment']['description'])]),
                experiment_type=str(this_library['experiment']['assay_term_name']),
                library_id=libid_new,
                notes=notes,
                )
            tosave_list.append(tosave_item)
    LibraryInfo.objects.bulk_create(tosave_list)


    end = time.time()
    print(end - start)
    print(library_id_list)

    # Finally, sequencings... ================================
    start = time.time()
    seq_list = []
    tosave_list = []
    for library in set(library_id_list):
        this_url = "https://www.encodeproject.org/"+library+"/?frame=embedded"
        response = requests.get(this_url, headers=headers)
        this_library = response.json()
        for rep in this_library['replicates']:
            this_rep_url = "https://www.encodeproject.org/"+rep+"/?frame=embedded"
            response = requests.get(this_rep_url, headers=headers)
            this_rep_library = response.json()
            target = re.split('/|-',str(this_rep_library['experiment']['target']))[2]

            default_label='_'.join([lib_sam[library],target])
            libraryinfo=LibraryInfo.objects.get(library_id=lib_new_name[library])

            this_uuid = str(this_rep_library['uuid'])
            notes=';'.join(['ENCODE uuid:'+this_uuid,'ENCODE url for files info:'+this_rep_url])

            existing_flag = 0
            for item in libraryinfo.seqinfo_set.all():
                if this_uuid == item.notes.split(';')[0].split(':')[1]:
                    existing_flag = 1
                    break;
                else:
                    existing_flag = 0
            if existing_flag == 0:
                counts = thislibrary.seqinfo_set.all().count()
                if counts == 0:
                    thisseqid = lib_new_name[library]
                else:
                    thisseqid = lib_new_name[library]+'_'+str(counts+1)
                tosave_item = SeqInfo(
                    default_label=default_label,
                    libraryinfo=libraryinfo,
                    seq_id=thisseqid,
                    notes=notes,
                    )
                tosave_list.append(tosave_item)
        SeqInfo.objects.bulk_create(tosave_list)


    end = time.time()
    print(end - start)


if __name__ == '__main__':
    main()

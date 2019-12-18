#!/usr/bin/env python
import os
import sys
import subprocess

#print(os.path.abspath(__file__))


def main():
    link = "https://www.encodeproject.org/search/\?type\=Experiment\&status\=released\&assay_title\=Histone+ChIP-seq\&biosample_ontology.term_name\=K562\&target.label\=H3K4me3\&target.label\=H3K36me3\&target.label\=H3K27me3\&target.label\=H3K27ac\&target.label\=H3K4me1"
    folder = '/Users/yuxinli/yxwork/gitrepo'
    #cmd1 = 'Rscript ./utility/encode_step1_grab_metadata_from_link.R ' + link + ' ' + folder
    cmd1 = 'Rscript encode_step1_grab_metadata_from_link.R ' + link + ' ' + folder

    print(cmd1)
    p = subprocess.call(cmd1,shell=True)
    samplefile = os.path.join(folder,'samples.tsv')
    libfile = os.path.join(folder,'libraries.tsv')
    seqfile = os.path.join(folder,'sequencings.tsv')
    data_sam = {}
    data_lib = {}
    data_seq = {}

    with open(samplefile, 'r') as f:
        for line in f:
            fields = line.strip('\n').split('\t')
            try:
                samdate = datetransform(fields[0].strip())
            except:
                samdate = None
            gname = fields[1].strip() if fields[1].strip() not in ['NA','N/A'] else ''        

            sampleid = fields[8].strip()
            samdescript = fields[9].strip()
            samspecies = fields[10].split('(')[0].lower().strip()
            samtype = fields[11].split('(')[0].strip().lower()
            samnotes = fields[20].strip()
            data_sam[sampleid] = {}
            data_sam[sampleid] = {
                'group':gname,
                'species': samspecies,
                'sample_type': samtype,
                'notes': samnotes,
            }
    print(data_sam)


    with open(libfile, 'r') as f:
        for line in f:
            fields = line.strip('\n').split('\t')
            sampleid = fields[0].strip()
            lib_des = fields[1].strip()
            username_tm = parser.parse_args().user
            libexp = fields[5].strip()
            libid = fields[8].strip()
            libnote = fields[9].strip()
            #thissample = SampleInfo.objects.get(sample_id=sampleid)
            # existing_flag = 0
            # for item in thissample.libraryinfo_set.all():
            #     if libid == item.notes.split(';')[0]:
            #         obj = item
            #         lib_new_name[libid] = item.library_id
            #         existing_flag = 1
            #         break;
            #     else:
            #         existing_flag = 0
            # lib_ids = list(LibraryInfo.objects.values_list('library_id', flat=True))
            # maxid = max([int(x.split('_')[1]) for x in lib_ids if x.startswith('ENCODE')])
            # libid_new = '_'.join(['ENCODE', str(maxid+1)])
            # lib_new_name[libid] = libid_new
            data_lib[libid] = {}
            data_lib[libid] = {
                'sampleinfo': sampid,
                'lib_description': lib_des,
                'experiment_type': libexp,
                'notes': libnote,
            }
    print(data_lib)

    with open(seqfile, 'r') as f:
        for line in f:
            fields = line.strip('\n').split('\t')
            seqid = fields[15].strip().split(';')[0].split(')')[1]
            #thislibary =  LibraryInfo.objects.get(library_id=lib_new_name[fields[5].strip()])
            #existing_flag = 0
            read_length = fields[10].strip()
            read_type = fields[11].strip()
            notes = ';'.join([fields[5].strip()+':'+fields[6].strip(),fields[15].strip()])
            # for item in thislibary.seqinfo_set.all():
            #     if seqid == item.notes.split(';')[1].split(')')[1]:
            #         obj = item
            #         existing_flag = 1
            #         writelines.append('\t'.join([item.seq_id,'1',fields[11].strip(),fields[16].strip()]))
            #         break;
            #     else:
            #         existing_flag = 0
            # if existing_flag == 0:
            #     counts = thislibary.seqinfo_set.all().count()
            #     if counts == 0:
            #         thisseqid = lib_new_name[fields[5].strip()]
            #     else:
            #         thisseqid = lib_new_name[fields[5].strip()]+'_'+str(counts+1)          
            data_seq[seqid] = {}
            data_seq[seqid] = {
                'sampleinfo': sampid,
                'library_id': lib_new_name[fields[5].strip()],
                'read_length':read_length,
                'read_type':read_type,
                'notes':notes,

            }
    print(data_seq)


    # if 'Preview' in request.POST:
    #     displayorder_sam = ['sample_id','sample_index','group','description', \
    #      'date','species', 'sample_type','notes','team_member']
    #     displayorder_lib = ['lib_id','sampleinfo','lib_description','team_member_initails', 'experiment_index', \
    #     'experiment_type', 'notes']
    #     displayorder_seq = ['seq_id','libraryinfo', 'default_label', 'team_member_initails', 'read_length',
    #                         'read_type','notes']

    #     context = {
    #         'encode_add_form': encode_add_form,
    #         'modalshow': 1,
    #         'displayorder_sam': displayorder_sam,
    #         'displayorder_lib': displayorder_lib,
    #         'displayorder_seq': displayorder_seq,
    #         'data_sam': data_sam,
    #         'data_lib':data_lib,
    #         'data_seq':data_seq,
    #     }        
    #     return render(request, 'masterseq_app/encode.html', context)
    #  if 'Save' in request.POST:
    #     for k, v in data_sam.items():
    #         if v['group']:
    #             group_tm = Group.objects.get(name=v['group'])
    #         else:
    #             group_tm = None 
    #         SampleInfo.objects.create(
    #             sample_id=k,
    #             species=v['species'],
    #             sample_type=v['sample_type '],
    #             notes=v['notes'],
    #             group=group_tm,
    #             )
    #     for k,v in data_lib.items():
    #         LibraryInfo.objects.create(
    #             library_id=k,
    #             sampleinfo=SampleInfo.objects.get(
    #                     sample_id=v['sampleinfo']),
    #             library_description=v['lib_description'],
    #             experiment_type=v['experiment_type'],
    #             notes=v['notes'],
    #             )
    #     for k,v in data_seq.items():
    #         SeqInfo.objects.create(
    #             seq_id=k,
    #             libraryinfo=LibraryInfo.objects.get(
    #                     library_id=v['library_id']),
    #             read_length=v['read_length'],
    #             read_type=v['read_type'],
    #             notes=v['notes'],
    #             )
    # context = {
    #     'encode_add_form': encode_add_form,
    # }

    # return render(request, 'masterseq_app/encode.html', context)




if __name__ == '__main__':
    main()

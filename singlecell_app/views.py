from django.shortcuts import render
from masterseq_app.models import LibraryInfo, SeqInfo
from django.conf import settings
import os
import random


# Create your views here.

'''
To add a column to scIndex or AllScLibs of libraryModel info, simply add the title of the coloumn wanted and the field name into a tuple
in header
list, eg ('Title of column', 'field_name')
'''

#hold all single cell experiment values
SINGLE_CELL_EXPS = ['10xATAC','scRNA-seq','snRNA-seq', 'scATAC-seq']

def scIndex(request):    
    #library_list = LibraryInfo.objects.filter(experiment_type='10xATAC').order_by('-date_started')
    library_list = LibraryInfo.objects.filter(experiment_type__in=SINGLE_CELL_EXPS, team_member_initails=request.user).values().order_by('-date_started')
    print('lib list: ', library_list)
    header = [
        ('Library ID', 'library_id'),
        ('Library Description', 'library_description'),
        ('Sample Info', 'sampleinfo_id'),
        ('Experiment Type','experiment_type'),
        ('Date Started' ,'date_started'),
        ('Date Completed' ,'date_completed'),
        ('CoolAdmin','CoolAdmin')
    ]

    library_lists = BuildList(library_list, header)
    print(library_lists)
    
    context = {
        'type' : 'My Single Cell Libraries',
        'header' : header,
        'library_lists': library_lists,
    }
    return render(request, 'singlecell_app/scIndex.html', context)

def AllScLibs(request):
    #library_list = LibraryInfo.objects.filter(experiment_type='10xATAC').order_by('-date_started')
    library_list = LibraryInfo.objects.select_related('User').filter(experiment_type__in=SINGLE_CELL_EXPS).values().order_by('-date_started')
    print('lib list: ', library_list)
    header = [
        ('Library ID', 'library_id'),
        ('Library Description', 'library_description') ,
        ('Sample Info', 'sampleinfo_id'),
        ('Experiment Type','experiment_type'),
        ('Date Started' ,'date_started'),
        ('Date Completed' ,'date_completed'),
    ]
    library_lists = BuildList(library_list, header)
    print(library_lists)
    context = {
        'type' : 'All Single Cell Libraries',
        'header' : header,
        'library_lists': library_lists,
    }
    return render(request, 'singlecell_app/scIndex.html', context)

'''Use to build library lists
'''
def BuildList(item_list, header):
    lists = []
    for item in item_list:
        properties = {}
        for head in header:
            try:
                property = item[head[1]]
                properties[head[1]] = property
            except:
                print('property not found: ', head[1])
                properties[head[1]] = ''
        lists.append(properties)
    return lists

def find10xStatus(seq_ids):
    tenxdir = settings.TENX_DIR
    tenx_output_folder = 'outs'
    tenx_target_outfile = 'web_summary.html'

    tenxstatus = []
    print('in tenx function')
    for seq in seq_ids:
        seq = str(seq)
        print(f'seq:{seq}')
        if not os.path.isdir(os.path.join(tenxdir, seq)):
            tenxstatus.append(False)
        else:
            if not os.path.isfile( os.path.join( tenxdir, seq, tenx_output_folder, tenx_target_outfile) ):
                tenxstatus.append(False)
            else:
                tenxstatus.append(True)
    return tenxstatus

def findSeqStatus(seq_ids):
    fastqdir = settings.FASTQ_DIR
    seqsStatus=[]
    for seq in seq_ids:
        seq_id = seq.seq_id
        reps =  seq_id.split('_')[2:]
        mainname = '_'.join(seq_id.split('_')[0:2])
        #rep is brandon_210_2 or brandon_210_3 in brandon_210_1_2_3
        print(reps)
        if len(reps) == 0:
            print('main: ',mainname)
        else:
            for rep in reps:
                if rep == '1':
                    print(rep)
                    if seq.read_type == 'PE':
                        r1 = mainname + 'R1_fastq.gz'
                        r2 = mainname +'_R2.fastq.gz'
                        if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                            seqsStatus.append('No')
                        else:
                            seqs10xStatus.append('Yes')
                    else:
                        r1 = mainname+'.fastq.gz'
                        r1op = item+'_R1.fastq.gz'
                        if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                            seqsStatus.append('No')
                        else: 
                            seqsStatus.append('Yes')

                else:
                    #find mainname_rep
                    print(rep)
                    repname = mainname + '_' + rep
                    if seq.read_type == 'PE':
                        r1 = repname + 'R1_fastq.gz'
                        r2 = repname +'_R2.fastq.gz'
                        if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                            seqsStatus.append('No')
                        else:
                            seqs10xStatus.append('Yes')
                    else:
                        r1 = repname+'.fastq.gz'
                        r1op = item+'_R1.fastq.gz'
                        if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                            seqsStatus.append('No')
                        else:                    
                            seqsStatus.append('Yes')
    return seqsStatus

'''Use to build seq lists
'''
def BuildSeqList(seqs_list, header):
    seqs_info = []
    seqsStatus = findSeqStatus(seqs_list)
    seqs10xStatus = find10xStatus(seqs_list)
    i = 0
    for seq in seqs_list:
        properties = {}
        properties['libraryinfo_id'] = seq.libraryinfo_id
        properties['seq_id'] = seq.seq_id
        properties['experiment_type'] = seq.libraryinfo.experiment_type
        properties['date_submitted_for_sequencing'] = seq.date_submitted_for_sequencing
        properties['Sequence Status'] = seqsStatus[i]
        properties['10xProcessed'] = seqs10xStatus[i]
        properties['CoolAdmin'] = FindCoolAdminStatus(seq)
        seqs_info.append(properties)
        i+=1

    return seqs_info

def FindCoolAdminStatus(seq):
    i = random.randint(1,10)
    #do something
    if i > 7:
        return 'No'
    elif i > 4:
        return 'Yes'
    else: 
        return 'Submitted'

def AllSeqs(request):
    seqs_list = SeqInfo.objects.filter(libraryinfo__experiment_type__in=SINGLE_CELL_EXPS).select_related('libraryinfo')
    
    header = [
        ('Sequence ID','seq_id'),
        ('Library ID', 'libraryinfo_id'),
        ('Experiment Type','experiment_type'),
        ('Date Submitted for Sequencing' ,'date_submitted_for_sequencing'),
        ('Sequence Status' ,'Sequence Status'),
        ('10xProcessed','10xProcessed'),
        ('CoolAdmin', 'CoolAdmin')
    ]
    print(seqs_list)
    seqs_info = BuildSeqList(seqs_list, header)
    print(seqs_info)
    # this for loop we will get 10xProcessed status, sequence status, and Experiment type 
    print(seqs_info)
   
    context = {
        'type':'All Sequences',
        'header': header,
        'seqs_info': seqs_info,
    }
    return render(request,'singlecell_app/seqs.html',context)

def MySeqs(request):
    header = [
        ('Sequence ID','seq_id'),
        ('Library ID', 'libraryinfo_id'),
        ('Experiment Type','experiment_type'),
        ('Date Submitted for Sequencing' ,'date_submitted_for_sequencing'),
        ('Sequence Status' ,'Sequence Status'),
        ('10xProcessed','10xProcessed'),
        ('CoolAdmin', 'CoolAdmin')
    ]
    seqs_list = SeqInfo.objects.filter(libraryinfo__experiment_type__in=SINGLE_CELL_EXPS, team_member_initails=request.user).select_related('libraryinfo')
    seqs_info = BuildSeqList(seqs_list, header)
    context = {
        'type':'My Sequences',
        'header': header,
        'seqs_info': seqs_info,
    }
    return render(request,'singlecell_app/seqs.html',context)


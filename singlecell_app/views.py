from django.shortcuts import render
from masterseq_app.models import LibraryInfo, SeqInfo
from django.conf import settings
import os
import random
import subprocess

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
    ids = [lib['id'] for lib in library_list]
    header = [
        ('Library ID', 'library_id'),
        ('Library Description', 'library_description'),
        ('Sample Info', 'sampleinfo_id'),
        ('Experiment Type','experiment_type'),
        ('Date Started' ,'date_started'),
        ('Date Completed' ,'date_completed'),
    ]
    library_lists = BuildList(library_list, header)
    context = {
        'type' : 'My Single Cell Libraries',
        'header' : header,
        'library_lists': library_lists,
        'ids': ids
    }
    print(ids)
    return render(request, 'singlecell_app/scIndex.html', context)


def AllScLibs(request):
    #library_list = LibraryInfo.objects.filter(experiment_type='10xATAC').order_by('-date_started')
    library_list = LibraryInfo.objects.select_related('User').filter(experiment_type__in=SINGLE_CELL_EXPS).values().order_by('-date_started')
    header = [
        ('Library ID', 'library_id'),
        ('Library Description', 'library_description') ,
        ('Sample Info', 'sampleinfo_id'),
        ('Experiment Type','experiment_type'),
        ('Date Started' ,'date_started'),
        ('Date Completed' ,'date_completed'),
    ]
    library_lists = BuildList(library_list, header)
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


def TenXPipelineCheck(seq):
    tenx_output_folder = 'outs'
    tenx_target_outfile = 'web_summary.html'
    tenxdir = settings.TENX_DIR
    path = os.path.join(tenxdir, str(seq))
    #first check if there is an .inqueue then an .inprocess 
    
    if not os.path.isdir(path):
        seqstatus = 'No'
    elif os.path.isfile(path + '/.inqueue'):
        seqstatus = 'In Queue'
    elif os.path.isfile( path + '/.inprocess' ):
        seqstatus = 'In Process'
    elif os.path.isfile( path + '/outs/_errors' ):
        seqstatus = 'Error!'
    else:
        if not os.path.isfile( os.path.join( path,
                tenx_output_folder, tenx_target_outfile ) ):
                seqstatus = 'No' 
        elif os.path.isfile(os.path.join( path, tenx_output_folder, tenx_target_outfile ) ):
            seqstatus = 'Yes'
        else:
            seqstatus = 'No'
    print(f'seq: {seq}, 10xstatus: {seqstatus}')
    return seqstatus


def findSeqStatus(seq_ids):
    fastqdir = settings.FASTQ_DIR
    seqsStatus=[]
    for seq in seq_ids:
        print(f'seq: {seq}, seqid: {seq.seq_id}, readtype: {seq.read_type}')
        seq_id = seq.seq_id
        reps =  seq_id.split('_')[2:]
        mainname = '_'.join(seq_id.split('_')[0:2])
        #reps are [_2] in brandon_210_2 or [_1,_2,_3] in brandon_210_1_2_3
        if len(reps) == 0:
            if seq.read_type == 'PE':
                r1 = mainname + 'R1_fastq.gz'
                r2 = mainname +'_R2.fastq.gz'
                if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                    seqsStatus.append('No')
                else:
                    seqsStatus.append('Yes')
            else:
                r1 = mainname+'.fastq.gz'
                r1op = mainname+'_R1.fastq.gz'
                if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                    seqsStatus.append('No')
                else: 
                    seqsStatus.append('Yes')
        else:
            for rep in reps:
                if rep == '1':
                    if seq.read_type == 'PE':
                        r1 = mainname + '_R1.fastq.gz'
                        r2 = mainname +'_R2.fastq.gz'
                        if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                            seqsStatus.append('No')
                        else:
                            seqsStatus.append('Yes')
                    else:
                        r1 = mainname+'.fastq.gz'
                        r1op = mainname+'_R1.fastq.gz'
                        if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                            seqsStatus.append('No')
                        else: 
                            seqsStatus.append('Yes')

                else:
                    #find mainname_rep
                    repname = mainname + '_' + rep
                    if seq.read_type == 'PE':
                        r1 = repname + '_R1.fastq.gz'
                        r2 = repname +'_R2.fastq.gz'
                        if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                            seqsStatus.append('No')
                        else:
                            seqsStatus.append('Yes')
                    else:
                        r1 = repname+'.fastq.gz'
                        r1op = repname+'_R1.fastq.gz'
                        if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                            seqsStatus.append('No')
                        else:                    
                            seqsStatus.append('Yes')
    print(f'seqstatus: {seqsStatus}')
    return seqsStatus


'''Use to build seq lists
'''
def BuildSeqList(seqs_list, request):
    seq_ids = [seq.seq_id for seq in seqs_list]
    libraryinfoIds = [ seq.libraryinfo_id for seq in seqs_list]
    experiment_types = [seq.libraryinfo.experiment_type for seq in seqs_list]
    submitted_dates = [seq.date_submitted_for_sequencing for seq in seqs_list ]
    seq_statuses = findSeqStatus(seqs_list)
    seqs10xStatus = [ TenXPipelineCheck(seq) for seq in seqs_list ] 
    coolAdmin = [FindCoolAdminStatus(seq) for seq in seqs_list]
    
    if request.user.is_staff == True:
        ownerList = [True for seq in seqs_list ]
    else:
        ownerList = [ 'NotOwner' for seq in seqs_list]

    print(ownerList)
    seqs_info = zip(seq_ids, libraryinfoIds, experiment_types, submitted_dates, 
                    seq_statuses, seqs10xStatus, coolAdmin, ownerList)
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
    if request.method == 'POST':
        seq = str(request.POST.get("buttonTenX"))
        print("seq posted: ", seq)
        SubmitToTenX(seq, request.user.email)
    
    seqs_list = SeqInfo.objects.filter(libraryinfo__experiment_type__in=SINGLE_CELL_EXPS).select_related('libraryinfo')
    header = [
        'Sequence ID', 'Library ID', 'Experiment Type', 'Date Submitted for Sequencing',
        'Sequence Status', '10xProcessed', 'CoolAdmin'
    ]
    seqs_info = BuildSeqList(seqs_list, request)
    context = {
        'type':'All Sequences',
        'header': header,
        'seqs_info': seqs_info,
    }
    return render(request,'singlecell_app/seqs.html',context)


def MySeqs(request):
    if request.method == 'POST':
        seq = str(request.POST.get("buttonTenX"))
        print("seq posted: ", seq)
        SubmitToTenX(seq, request.user.email)
    header = [
        'Sequence ID', 'Library ID', 'Experiment Type', 'Date Submitted for Sequencing',
        'Sequence Status', '10xProcessed', 'CoolAdmin'
    ]
    seqs_list = SeqInfo.objects.filter(libraryinfo__experiment_type__in=SINGLE_CELL_EXPS, team_member_initails=request.user).select_related('libraryinfo')
    seqs_info = BuildSeqList(seqs_list, request)
    context = {
        'type':'My Sequences',
        'header': header,
        'seqs_info': seqs_info,
    }
    return render(request,'singlecell_app/seqs.html',context)


def SubmitToTenX(seq, email):
    tenxdir = settings.TENX_DIR
    seq_info = list(SeqInfo.objects.filter(seq_id=seq).select_related(
        'libraryinfo__sampleinfo').values('seq_id',
        'libraryinfo__sampleinfo__species','read_type',
        'libraryinfo__experiment_type'))
    seqs = SplitSeqs(seq_info[0]['seq_id'])    
    genome =  seq_info[0]['libraryinfo__sampleinfo__species'] 
    
    #TODO check if this is a correct idea
    if genome.lower() == 'human':
        genome = 'hg38'
    else:
        genome = 'mm10'
    
    filename = '.'+str(seq)+'.tsv'
    tsv_writecontent = '\t'.join([seq, ','.join(seqs), genome]) 
    seqDir = os.path.join(tenxdir,seq)
    if not os.path.exists(seqDir):
        os.mkdir(seqDir)
    tsv_file = os.path.join(seqDir, filename)
    with open(tsv_file, 'w') as f:
        f.write(tsv_writecontent)
    cmd1 = './utility/run10xOnly_local.sh ' + seq +' ' + tenxdir + ' ' + email
    p = subprocess.Popen(
        cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def SplitSeqs(seq):
    splt = seq.split('_')
    addlseqs = []
    basename = ('_').join(splt[:2])
    if len(splt) < 3:
        #do nothing special
        return [basename]
    else:
        for addlseq in splt[2:]:
            if addlseq == '1':
                addlseqs.append(basename)
            else:
                addlseqs.append(basename+'_'+addlseq)
    return addlseqs

from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from django.forms.models import model_to_dict
from django.core import serializers
from django.http import JsonResponse
from masterseq_app.models import LibraryInfo, SeqInfo
from .forms import CoolAdminForm
from .models import CoolAdminSubmission
from django.conf import settings
import os
import random
import subprocess
import json
from epigen_ucsd_django.shared import *

# Create your views here.



#hold all single cell experiment values
SINGLE_CELL_EXPS = ['10xATAC','scRNA-seq','snRNA-seq', 'scATAC-seq']

#TODO follow up with frank about this mapping and how people will choose the ref genome
SPECIES_MAP = {
    'human': 'hg38',
    'mouse': 'mm10',
}

#view to return All sequences
def AllSeqs(request):
    form = CoolAdminForm()
    seqs_list = SeqInfo.objects.filter(libraryinfo__experiment_type__in=SINGLE_CELL_EXPS).select_related('libraryinfo').order_by('date_submitted_for_sequencing')
    header = [
        'Sequence ID', 'Library ID', 'Experiment Type', 'Date Submitted for Sequencing',
        'Sequence Status', '10xProcessed', 'CoolAdmin'
    ]
    seqs_info = BuildSeqList(seqs_list, request, False)
    context = {
        'type':'All Sequences',
        'header': header,
        'seqs_info': seqs_info,
        'email':  request.user.email,
        'form' : form,
    }
    return render(request,'singlecell_app/seqs.html',context)

#view to return user specific sequences
def MySeqs(request):
    form = CoolAdminForm()
    header = [
        'Sequence ID', 'Library ID', 'Experiment Type', 'Date Submitted for Sequencing',
        'Sequence Status', '10xProcessed', 'CoolAdmin'
    ]
    seqs_list = SeqInfo.objects.filter(libraryinfo__experiment_type__in=SINGLE_CELL_EXPS, team_member_initails=request.user).select_related('libraryinfo').order_by('date_submitted_for_sequencing')
    seqs_info = BuildSeqList(seqs_list, request, True)
    context = {
        'type':'My Sequences',
        'header': header,
        'seqs_info': seqs_info,
        'email':  request.user.email,
        'form' : form,

    }
    return render(request,'singlecell_app/seqs.html',context)

'''
This function returns a string that represents 
the status that the sequence is in the 10x pipeline.
@params
    seq: a string that represents the sequence name to be checked.
@returns
    string 'No' when sequence is not submitted
    string 'In Queue' when sequence is in the qsub queue
    string 'In Process' when sequence is being processed by 10x pipeline
    string 'Error' when an error occurs in pipeline
    string 'Yes' when the 10x pipeline is succesfully done

'''
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
    return seqstatus

'''#TODO maybe a dictionary would be better suited for this to not be order dependent
This function checks the FASTQ sequence status and returns the results in a string array. 
Order dependent.
@params
    seq_ids: an array of seq strings. seq string represents a sequence to be checked.
@returns
    returns an array of strings representing the status of the sequence.
    'Yes': FASTQ files present
    'No': no FASTQ files present
'''
def findSeqStatus(seq_ids):
    fastqdir = settings.FASTQ_DIR
    seqsStatus=[]
    for seq in seq_ids:
        #print(f'seq: {seq}, seqid: {seq.seq_id}, readtype: {seq.read_type}')
        seq_id = seq.seq_id
        reps =  seq_id.split('_')[2:]
        mainname = '_'.join(seq_id.split('_')[0:2])
        #reps are [_2] in brandon_210_2 or [_1,_2,_3] in brandon_210_1_2_3
        if len(reps) == 0:
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
            for rep in reps:
                if rep == '1':
                    if seq.read_type == 'PE':
                        r1 = mainname + '_R1.fastq.gz'
                        r2 = mainname +'_R2.fastq.gz'
                        if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                            seqsStatus.append('No')
                            break
                    else:
                        r1 = mainname+'.fastq.gz'
                        r1op = mainname+'_R1.fastq.gz'
                        if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                            seqsStatus.append('No')
                            break
                else:
                    #find mainname_rep
                    repname = mainname + '_' + rep
                    if seq.read_type == 'PE':
                        r1 = repname + '_R1.fastq.gz'
                        r2 = repname +'_R2.fastq.gz'
                        if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                            seqsStatus.append('No')
                            break
                    else:
                        r1 = repname+'.fastq.gz'
                        r1op = repname+'_R1.fastq.gz'
                        if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                            seqsStatus.append('No')
                            break
            seqsStatus.append('Yes')
    #print(f'seqstatus: {seqsStatus}')
    return seqsStatus

'''
This function is used to build seq lists to be returned to the html template.
@params
    seqs_list is an array of strings each string is a single cell smaple sequence.
@returns
    returns a zipped list of data describing the sequence processed.
    #TODO clean this function up, library IDs not necessary anymore?
'''
def BuildSeqList(seqs_list, request, owner):
    seq_ids = [seq.seq_id for seq in seqs_list] #0
    libraryinfoIds = [ seq.libraryinfo.library_id for seq in seqs_list] #1
    libraryIds = [ seq.libraryinfo_id for seq in seqs_list]#2
    experiment_types = [seq.libraryinfo.experiment_type for seq in seqs_list]#3
    submitted_dates = [ str(seq.date_submitted_for_sequencing) for seq in seqs_list ]#4
    seq_statuses = findSeqStatus(seqs_list)#5
    seqs10xStatus = [ TenXPipelineCheck(seq) for seq in seqs_list ] #6
    coolAdmin = [FindCoolAdminStatus(seq) for seq in seqs_list] #7
    links = [] #8
    #build lit of links
    for seq in seqs_list:
        if FindCoolAdminStatus(seq) == '.status.success':
            links.append(getCoolAdminLink(seq))
        else:
            links.append('')
    #build list if sequence is 'owned' this means it will be clickable by user
    if is_member(request.user,['bioinformatics']) or owner == True:
        ownerList = ['Owner' for seq in seqs_list ]
    else:
        ownerList = []
        for seq in seqs_list:
            if(request.user == seq.team_member_initails):
                ownerList.append('Owner')
            else:
                ownerList.append('NotOwner')
    seqs_info = zip(seq_ids, libraryinfoIds, libraryIds, experiment_types, submitted_dates, 
                    seq_statuses, seqs10xStatus, coolAdmin, ownerList, links)
    return seqs_info

'''
'''
def FindCoolAdminStatus(seq):
    coolAdminDir = settings.COOLADMIN_DIR
    
    subExists = CoolAdminSubmission.objects.filter(seqName=seq, status='ClickToSubmit').exists()
    #check if folder exists in coolAdminDir
    path = os.path.join(coolAdminDir, str(seq))
    #if exists check which status file is present and return that
    #do something
    if not os.path.isdir(path) or subExists == True:
        return 'ClickToSubmit'
    elif os.path.isfile(path + '/.status.success'):
        return '.status.success'
    elif os.path.isfile(path + '/.status.processing'):
        return '.status.processing'
    elif os.path.isfile(path + '/.status.fail'):
        return '.status.fail'
    else: 
        return 'Submitted'


def SubmitSingleCell(request):
    #print(request)
    email = request.POST.get('email')
    seq = request.POST.get('seq') 
    status = SubmitToTenX(seq, email)
    if status:
        data = {
            'is_submitted' : True
        }
    else:
        data = {
            'is_submitted' : False
        }
    return JsonResponse(data)

'''
This function handles a cooladmin submission request from LIMS user.
This function run a bash script ./utility/coolAdmin.sh
'''
def SubmitToCoolAdmin(request):
    print('submitting cool admin job')
    email = request.POST.get('email')
    seq = request.POST.get('seq')
    info = SeqInfo.objects.select_related('libraryinfo__sampleinfo').get(seq_id=seq)
    species = SPECIES_MAP[info.libraryinfo.sampleinfo.species.lower()]
    submission, created = CoolAdminSubmission.objects.update_or_create(seqName=seq,
                        defaults={
                            'seqName':seq,
                            'species':species,
                            'status':'inProcess',
                            'seqinfo':info, 
                            'date_submitted':datetime.now()
                            })
    
    print(model_to_dict(submission))
    cmd1 = f'./utility/coolAdmin.sh {email} {seq} {species}'
    
   # p = subprocess.Popen(
    #    cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data ={
        'success':'submitted'
    }
    return JsonResponse(data, safe=False)

def EditCoolAdminSubmission(request, seqinfo):
    seqinfo_id = get_object_or_404(SeqInfo, seq_id=seqinfo)
    
    if not seqinfo_id or (not request.user.groups.filter(name='bioinformatics').exists() or request.user != seqinfo_id.team_member_initails):
        raise PermissionDenied
    
    info = SeqInfo.objects.select_related('libraryinfo__sampleinfo').get(seq_id=seqinfo_id)
    species = SPECIES_MAP[info.libraryinfo.sampleinfo.species.lower()]

    #starter_data for initialization values of CoolAdminSubmissionForm 
    starter_data = {
            'seqName': seqinfo,
            'species': species,
            'seqinfo': seqinfo_id,
            }
    
    submission = False
  
    #get previous cool admin submission if exists
    if CoolAdminSubmission.objects.filter(seqinfo=seqinfo_id).exists():
        submission = CoolAdminSubmission.objects.get(seqinfo=seqinfo_id)
        form = CoolAdminForm(initial=model_to_dict(submission))
        print(f'previous submission:{model_to_dict(submission)} ')
    else:#create a form with starter data if no previous submission form
        form = CoolAdminForm(initial=starter_data)
   
    #handle submission of new submission form
    if request.method == 'POST':
        post = request.POST.copy()
        post['seqinfo'] = seqinfo_id
        post['species'] = species
        post['seqName'] = seqinfo
        #there has been a previous submission
        if(submission != False):
            form = CoolAdminForm(post, initial=model_to_dict(submission))
            print('from: ',form.is_valid(), form.has_changed(),form.cleaned_data)
            if form.is_valid():
                if(form.has_changed()):
                    data = form.cleaned_data
                    data['status'] = 'ClickToSubmit'
                    print('changed data: ',form.changed_data)
                    CoolAdminSubmission.objects.filter(seqinfo=seqinfo_id).update(**data)
                else:
                    print('no changes to submission!')
            else:
                print('not valid!')
        else:
            #there was no previous submission but new data was posted: save these parameters if they are different from the defaults
            form = CoolAdminForm(post)
            if form.is_valid():
                data = form.cleaned_data
                data['seqinfo'] = seqinfo_id
                data['species'] = species 
                data['seqName'] = seqinfo
                obj = CoolAdminSubmission(**data)
                obj.save()
                print('new submission: ',model_to_dict(obj))
            
        return redirect('singlecell_app:myseqs')

    context = {
        'form' : form,
        'seq': seqinfo,
    }

    return render(request,'singlecell_app/editCoolAdmin.html', context)

def createCoolAdminSubmission(dict):
    submission = CoolAdminSubmission.objects.create_submission(dict)
    return submission

def getCoolAdminLink(seq):
    #cool_dir = f'/projects/ps-epigen/datasets/opoirion/output_LIMS/{seq}/repl1//repl1_{seq}_finals_logs.json'
    cool_dir = settings.COOLADMIN_DIR
    json_file = os.path.join(cool_dir, str(seq), f'repl1//repl1_{str(seq)}_final_logs.json')
    
    with open(json_file, 'r') as f:
        cool_data = f.read()
    cool_dict = json.loads(cool_data) 
    
    return (cool_dict['report_address'])

'''
This function should only be called by another fucntion that ensures the sequence is valid to be submitted
This function submits a sequence to 10x cell ranger pipeline
'''
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
    inqueue = os.path.join(seqDir, '.inqueue')
    with open(inqueue, 'w') as f:
        f.write('')
    tsv_file = os.path.join(seqDir, filename)
    with open(tsv_file, 'w') as f:
        f.write(tsv_writecontent)
    cmd1 = './utility/run10xOnly_local.sh ' + seq +' ' + tenxdir + ' ' + email
    p = subprocess.Popen(
        cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return True

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


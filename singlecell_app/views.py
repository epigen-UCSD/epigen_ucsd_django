from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth.models import User, Group
from datetime import datetime
from django.forms.models import model_to_dict
from django.core import serializers
from django.http import JsonResponse
from masterseq_app.models import LibraryInfo, SeqInfo, GenomeInfo
from .forms import CoolAdminForm
from .models import CoolAdminSubmission
from django.conf import settings
import os
import random
import subprocess
import json
from epigen_ucsd_django.shared import *

#keys in snap param dict should be the same as the fields in the model and form.
SNAP_PARAM_DICT = {
    'pipeline_version':'VERSION',
    'useHarmony':'USEHARMONY',
    'snapUsePeak':'SNAPUSEPEAK',
    'snapSubset':'SNAPSUBSET',
    'doChromVar':'DOCHROMVAR',
    'readInPeak':'READINPEAK',
    'tssPerCell':'TSSPERCELL',
    'minReadPerCell':'MINREADPERCELL',
    'snapBinSize':'SNAPBINSIZE',
    'snapNDims':'SNAPNDIMS',
    'refgenome':'GENOMETYPE',
}

#hold all single cell experiment values
SINGLE_CELL_EXPS = ['10xATAC','scRNA-seq','snRNA-seq', 'scATAC-seq']

defaultgenome = {'human': 'hg38', 'mouse': 'mm10',
                 'rat': 'rn6', 'cattle': 'ARS-UCD1.2'}

#view returns All sequences
def AllSeqs(request):
    context ={
        'type':'All Sequences',
        'AllSeq': True
    }
    if request.user.groups.filter(name='bioinformatics').exists():
        context['BioUser'] = True
        print(context)
        return render(request, 'singlecell_app/myseqs.html', context)
    else:
        context['BioUser'] = False
        print(context)
        return render(request, 'singlecell_app/myseqs.html', context)


#view returns myseqs.html which displays only  user's seqs
def MySeqs(request):
    context ={
        'type':'My Sequences',
        'AllSeq': False
    }
    return render(request, 'singlecell_app/myseqs.html', context)

""" async function to get hit by ajax. Returns json of all single cell data dict
in db
"""
def AllSingleCellData(request):
    #make sure only bioinformatics group users allowed

    seqs_queryset = SeqInfo.objects.filter(libraryinfo__experiment_type__in=\
        SINGLE_CELL_EXPS).select_related('libraryinfo',).order_by(\
        'date_submitted_for_sequencing').values('id','seq_id', 'libraryinfo__experiment_type','read_type','libraryinfo__sampleinfo__species')

    data = list(seqs_queryset)
    build_seq_list(data)
    print('new data: ',data)
    return JsonResponse(data, safe=False)

"""async function to get hit by ajax, returns user only seqs
"""
def UserSingleCellData(request):
    seqs_queryset = SeqInfo.objects.filter(libraryinfo__experiment_type__in=\
        SINGLE_CELL_EXPS,team_member_initails=request.user).select_related('libraryinfo','libraryinfo__sampleinfo').order_by(\
        'date_submitted_for_sequencing').values('id','seq_id', 'libraryinfo__experiment_type','read_type','libraryinfo__sampleinfo__species')

    data = list(seqs_queryset)
    build_seq_list(data)
    return JsonResponse(data, safe=False)

'''
This function is used to build seq lists to be returned to the from an AJAX call for AllSeqs2.
@params
    seqs_list is a list of dictionaires where each has the seq_id and experiment_type for a single cell sample sequence.
@returns
    returns a list of dictionaries with more information describing the sequence.
    #TODO clean this function up, library IDs not necessary anymore
'''
def build_seq_list(seqs_list):
    #print(seqs_list)
    for entry in seqs_list:
        seq_id = entry['seq_id']
        entry['seq_status'] = find_seq_status(seq_id, entry['read_type'])
        entry['10x_status'] = tenX_pipeline_check(seq_id)
        entry['species'] = entry['libraryinfo__sampleinfo__species']
        entry['cooladmin_status'] = find_cooladmin_status(entry['id'])
        entry['link'] = get_cooladmin_link(seq_id)
    return (seqs_list)

"""This function returns a string that represents 
the status of parameter seq in the 10x pipeline.
@params
    seq: a string that represents the sequence name to be checked.
@returns
    string 'No' when sequence is not submitted
    string 'In Queue' when sequence is in the qsub queue
    string 'In Process' when sequence is being processed by 10x pipeline
    string 'Error' when an error occurs in pipeline
    string 'Yes' when the 10x pipeline is succesfully done
"""
def tenX_pipeline_check(seq):
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

"""This function checks the FASTQ sequence status and returns the results 
@params
    seq_id: string represents a seq_id to be checked.
    read_type: Paired end or not
@returns
    'Yes': FASTQ files present
    'No': no FASTQ files present
"""
def find_seq_status(seq_id, read_type):
    fastqdir = settings.FASTQ_DIR
    #print(f'seq: {seq}, seqid: {seq.seq_id}, readtype: {seq.read_type}')
    reps =  seq_id.split('_')[2:]
    mainname = '_'.join(seq_id.split('_')[0:2])
    #reps are [_2] in brandon_210_2 or [_1,_2,_3] in brandon_210_1_2_3
    if len(reps) == 0:
        if read_type == 'PE':
            r1 = mainname + '_R1.fastq.gz'
            r2 = mainname +'_R2.fastq.gz'
            if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                seqsStatus = ('No')
            else:
                seqsStatus = ('Yes')
        else:
            r1 = mainname+'.fastq.gz'
            r1op = mainname+'_R1.fastq.gz'
            if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                seqsStatus = 'No'
            else: 
                seqsStatus = 'Yes'
    else:
        for rep in reps:
            if rep == '1':
                if read_type == 'PE':
                    r1 = mainname + '_R1.fastq.gz'
                    r2 = mainname +'_R2.fastq.gz'
                    if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                        return( 'No' )
                else:
                    r1 = mainname+'.fastq.gz'
                    r1op = mainname+'_R1.fastq.gz'
                    if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                        return('No')
            else:
                #find mainname_rep
                repname = mainname + '_' + rep
                if read_type == 'PE':
                    r1 = repname + '_R1.fastq.gz'
                    r2 = repname +'_R2.fastq.gz'
                    if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                        return ('No')
                else:
                    r1 = repname+'.fastq.gz'
                    r1op = repname+'_R1.fastq.gz'
                    if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                        return ('No')
                        
        #set when for loop statement terminates, all reps fastq's were present
        seqsStatus = 'Yes'
    #print(f'seqstatus: {seqsStatus}')
    return seqsStatus


# def BuildSeqList(seqs_list, request, owner):
#     #coolAdminSet = CoolAdminSubmission.objects.filter(seqinfo__in=seqs_list)
#     #print(f'cool admin submissions: {coolAdminSet}')
#     seq_ids = [seq.seq_id for seq in seqs_list] #0
#     experiment_types = [seq.libraryinfo.experiment_type for seq in seqs_list]#1
#     submitted_dates = [ str(seq.date_submitted_for_sequencing) for seq in seqs_list ]#2
#     seq_statuses = findSeqStatus(seqs_list)#3
#     seqs10xStatus = [ TenXPipelineCheck(seq) for seq in seqs_list ]#4
#     coolAdmin = [FindCoolAdminStatus(seq) for seq in seqs_list]#5
#     links = []#6
#     seqIds = [seq.id for seq in seqs_list]
    
#     #build list of links
#     for i in range(len(seqs_list)):
#         if coolAdmin[i] == '.status.success':
#             links.append(getCoolAdminLink( seq_ids[i] ))
#         else:
#             links.append('')
    
#     #build list if sequence is 'owned' this means it will be clickable by user
#     if Group.objects.get(name='bioinformatics') in model_to_dict(User.objects.get(username=request.user))['groups'] or owner == True:
#         ownerList = ['owner' for seq in seqs_list ]
#     else:
#         ownerList = []
#         for seq in seqs_list:
#             if(request.user == seq.team_member_initails): 
#                 ownerList.append('owner')
#             else:
#                 ownerList.append('not-owner')
    
#     seqs_info = zip(seq_ids, experiment_types, submitted_dates, 
#                     seq_statuses, seqs10xStatus, coolAdmin, ownerList, links, seqIds)
#     return seqs_info

'''
'''
def find_cooladmin_status(seq):
    coolAdminDir = settings.COOLADMIN_DIR
    clickToSub = CoolAdminSubmission.objects.filter(seqinfo=seq, status='ClickToSubmit').exists()
    #check if folder exists in coolAdminDir
    path = os.path.join(coolAdminDir, str(seq))

    #if no cool admin submitted before or if it has been but the parameters have been changed
    if not os.path.isdir(path) or clickToSub == True:
        return 'ClickToSubmit'
    
    elif os.path.isfile(path + '/.status.success'):
        return get_cooladmin_link(seq)
    elif os.path.isfile(path + '/.status.processing'):
        return '.status.processing'
    elif os.path.isfile(path + '/.status.fail'):
        return '.status.fail'
    else: 
        return 'submitted'


def submit_singlecell(request):
    seq = request.POST.get('seq') 
    seqinfo_id = get_object_or_404(SeqInfo, seq_id=seq)
    email = request.user.email
    status = submit_tenX(seq, email)
    data = {
        "is_submitted": True,
    }
    return JsonResponse(data)

'''
This function handles a cooladmin submission request from LIMS user.
This function run a bash script ./utility/coolAdmin.sh
'''
def submit_cooladmin(request):
    seq = request.POST.get('seq')
    email = request.user.email
    info = SeqInfo.objects.select_related('libraryinfo__sampleinfo').get(seq_id=seq)
    species = defaultgenome[info.libraryinfo.sampleinfo.species.lower()]
    
    defaults = {
                'status':'inProcess',
                'seqinfo':info, 
                'date_submitted':datetime.now(),
                'date_modified':datetime.now(),
                }
    
    submission, created = CoolAdminSubmission.objects.update_or_create(seqinfo=info,
                        defaults=defaults)
    submission_dict = model_to_dict(submission)
    if created == True:
        if(info.libraryinfo.sampleinfo.experiment_type_choice == '10xATAC'):
            submission_dict['refgenome'] = getReferenceUsed(seq)
        else:#set ref genome to default species
            submission_dict['refgenome'] =  species
            submission.refgenome = GenomeInfo.objects.create(genome_name=submission_dict['refgenome'],species=info.libraryinfo.sampleinfo.species.lower())
            submission.date_modified = datetime.now()
            submission.date_submitted = datetime.now()
            submission.save()   
    #convert key to refgenome
    #always use refgenome used in 10xATAC job
    else:
        print('submission dict: ',submission_dict)
        if(info.libraryinfo.sampleinfo.experiment_type_choice == '10xATAC'):
            submission_dict['refgenome'] =  getReferenceUsed(seq)
        else:
            submission_dict['refgenome'] = str(GenomeInfo.objects.get(id=submission_dict['refgenome']).genome_name)

    seqString = f'"{seq}"'

    paramString = buildCoolAdminParameterString(submission_dict)
    #print('paramString: ',paramString)
    cmd1 = f'./utility/coolAdmin.sh {email} {seqString} {paramString}'
    
    p = subprocess.Popen(
        cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data ={
        'is_submitted': True
    }
    return JsonResponse(data, safe=False)


"""This is a big boy here...
@header:
    This function will be hit by a request to 'save' a cooladmin form for editing
    submission parameters. This functions checks if the posted form data is
    different from the previous submission form submitted, if it is different then 
    the posted form is saved to the CoolAdminSubmission model.
    If there was no previous submission then a new object is created and saved.
@side-effects:
    If new form is saved then status of CoolAdminSubmission model will be changed to
    ClickToSubmit, this will cause the button to be displayed as clicktosubmit in 
    seqs.html.(pseudo overwriting previous results)
@params: 
    seqinfo is a string that represents the seq_id of SeqInfo model object.
@returns:
    redirects user if user POSTs 'save'
"""
#TODO write test for this function
def edit_cooladmin_sub(request, seqinfo):
    seqinfo_id = get_object_or_404(SeqInfo, seq_id=seqinfo)
    #print('edit reqeust: ',(request.user.groups.filter(name='bioinformatics').exists()))
    if(not request.user.groups.filter(name='bioinformatics').exists() and request.user != seqinfo_id.team_member_initails):
        print('raising exception')
        raise PermissionDenied
    
    seqinfo = SeqInfo.objects.select_related('libraryinfo__sampleinfo').get(seq_id=seqinfo_id)
    species = seqinfo.libraryinfo.sampleinfo.species
    exptType = seqinfo.libraryinfo.experiment_type
    #print("expt type: ", exptType)
    
    #starter_data for initialization values of CoolAdminSubmissionForm 
    starter_data = {
            'species': species,
            'seqinfo': seqinfo,
            }

    ref_genome_used = ""
    submission = False

    #get previous cool admin submission if exists
    if CoolAdminSubmission.objects.filter(seqinfo=seqinfo_id).exists():
        submission = CoolAdminSubmission.objects.get(seqinfo=seqinfo_id)
        #make form based on model values
        form = CoolAdminForm(initial=model_to_dict(submission), spec=species)
        #set the choice field based on the key of the tuple using the previous submission 
        if(exptType == '10xATAC'):#set ref genome if 10xATAC type of experiment
            ref_genome_used =  getReferenceUsed(seqinfo)
            form.fields['refgenome'].initial = [ref_genome_used]
        else:
            form.fields['refgenome'].initial = [submission.refgenome]
    else:#create a form with starter data if no previous submission form
        form = CoolAdminForm(initial=starter_data, spec=species)
        if(exptType == '10xATAC'):
            ref_genome_used =  getReferenceUsed(seqinfo)
            form.fields['refgenome'].initial = [ref_genome_used]
        else:
            form.fields['refgenome'].initial = [defaultgenome[species]]
    print('serving form: ',form)
    #handle save of new submission form
    if request.method == 'POST':
        post = request.POST.copy()
        print('post: ',post)
        post['seqinfo'] = seqinfo_id

        #overwrite refgenome to post data
        if(exptType == '10xATAC'):
            post['refgenome'] = ref_genome_used
        
        #if previous submission, compare to new submission
        if(submission != False):
            data = model_to_dict(submission)
            print('refgenome: ', data['refgenome'], data)
            data['genome'] = data['refgenome']
            #print('\n data: ',data)
            #print('\n post: ',post)
            form = CoolAdminForm(post, initial=data)
            #print('form: is valid and has changed: ',form.is_valid(), form.has_changed())
            if form.is_valid():
                if(form.has_changed()):
                    data = form.cleaned_data
                    data['status'] = 'ClickToSubmit'
                    print('changed data: ',form.changed_data)
                    CoolAdminSubmission.objects.filter(seqinfo=seqinfo_id).update(**data)
                    obj = CoolAdminSubmission.objects.get(seqinfo=seqinfo_id)
                    obj.date_modified = datetime.now()
                    obj.save()
                else:
                    print('no changes to submission!')
            else:
                print('form not valid!')
        else:
            #there was no previous submission but new data was posted: save these parameters if they are different from the defaults
            form = CoolAdminForm(post)
            if form.is_valid():
                data = form.cleaned_data
                data['seqinfo'] = seqinfo_id
                obj = CoolAdminSubmission(**data)
                obj.save()
                #print('new submission: ',model_to_dict(obj))
            
        return redirect('singlecell_app:myseqs')

    context = {
        'form' : form,
        'seq': seqinfo,
    }
    return render(request,'singlecell_app/editCoolAdmin.html', context)

"""Call this function when cooladmin status has already been confirmed to be success
"""
def get_cooladmin_link(seq):
    #cool_dir = f'/projects/ps-epigen/datasets/opoirion/output_LIMS/{seq}/repl1//repl1_{seq}_finals_logs.json'
    cool_dir = settings.COOLADMIN_DIR
    try:
        json_file = os.path.join(cool_dir, str(seq), f'repl1//repl1_{str(seq)}_final_logs.json')
        
        with open(json_file, 'r') as f:
            cool_data = f.read()
        cool_dict = json.loads(cool_data) 
        return (cool_dict['report_address'])
    except:
        return("")

"""This function should only be called by another fucntion that ensures the sequence is valid to be submitted
This function submits a sequence to 10x cell ranger pipeline
"""
def submit_tenX(seq, email):
    tenxdir = settings.TENX_DIR
    seq_info = list(SeqInfo.objects.filter(seq_id=seq).select_related(
        'libraryinfo__sampleinfo').values('seq_id',
        'libraryinfo__sampleinfo__species','read_type',
        'libraryinfo__experiment_type'))
    seqs = split_seqs(seq_info[0]['seq_id'])
    genome =  seq_info[0]['libraryinfo__sampleinfo__species'] 
    
    #TODO check if this is a correct idea
    if genome.lower() == 'human':
        genome = 'hg38'
    else:
        genome = 'mm10'

    #filename = ".sequence.tsv"
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

def split_seqs(seq):
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

#TODO do param error checking?
def buildCoolAdminParameterString(dict):
    print('dict: ',dict)
    paramString = ''
    for key in SNAP_PARAM_DICT.keys():
        paramString += f'{SNAP_PARAM_DICT[key]}="{dict[key]}",'
    return paramString

def getReferenceUsed(seq):
    """This function gets the ref genome used in 10x atac pipeline to use for cool admin submission
    @params seq is a string of the sequnece wanted e.g. seq="JYH_1047"
    @returns a string that is the refernce genome used
    """
    #To return
    refgenome = ''

    tenx_output_folder = 'outs'
    tenx_target_outfile = 'summary.json'
    tenxdir = settings.TENX_DIR

    file_path = os.path.join(tenxdir, str(seq), tenx_output_folder, tenx_target_outfile)

    with open(file_path) as json_file:
        data = json.load(json_file)
        refgenome = data["reference_assembly"]    
    #open summarry.json and read "reference_assembly"
    return refgenome


def getLatestModification(seq_object):
    """This function returns the latest modfication to the seq object
    """
    #check if user modified cooladmin submission params, check if user submitted either cooladmin OR 10xCellranger job
    #check if sequence status has updated? pipeline status's updates?
    print(1)
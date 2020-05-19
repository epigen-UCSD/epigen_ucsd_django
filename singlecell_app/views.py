from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth.models import User, Group
from datetime import datetime
from django.forms.models import model_to_dict
from django.core import serializers
from django.http import JsonResponse, FileResponse, HttpResponse
from masterseq_app.models import LibraryInfo, SeqInfo, GenomeInfo, RefGenomeInfo, ExperimentType
from epigen_ucsd_django.shared import is_member,is_in_multiple_groups

from .forms import CoolAdminForm
from .models import CoolAdminSubmission, SingleCellObject
from django.conf import settings
import os
import random
import string
import subprocess
import json
from epigen_ucsd_django.shared import *
import shutil


# keys in snap param dict should be the same as the fields in the model and form.
SNAP_PARAM_DICT = {
    'pipeline_version': 'VERSION',
    'useHarmony': 'USEHARMONY',
    'snapUsePeak': 'SNAPUSEPEAK',
    'snapSubset': 'SNAPSUBSET',
    'doChromVar': 'DOCHROMVAR',
    'readInPeak': 'READINPEAK',
    'tssPerCell': 'TSSPERCELL',
    'minReadPerCell': 'MINREADPERCELL',
    'snapBinSize': 'SNAPBINSIZE',
    'snapNDims': 'SNAPNDIMS',
    'refgenome': 'GENOMETYPE',
}

# hold all single cell experiment values
SINGLE_CELL_EXPS = ['10xATAC', 'scRNA-seq', 'snRNA-seq', 'scATAC-seq']

defaultgenome = {'human': 'hg38', 'mouse': 'mm10',
                 'rat': 'rn6', 'cattle': 'ARS-UCD1.2'}

LINK_CLASS_NAME="data-link-epigen"

INQUEUE = 'InQueue'



#TODO do rat for scRNA-seq plus option for hg19, we deafault to hg38 right now.
#TODO also need option for mixed mouse and human


def AllSeqs(request):
    """view returns all singlecell expt type sequences
    """
    context = {
        'type': 'All Sequences',
        'AllSeq': True
    }
    if not is_in_multiple_groups(request.user,['wetlab','bioinformatics']):
        raise PermissionDenied
    if request.user.groups.filter(name='bioinformatics').exists():
        context['BioUser'] = True
        return render(request, 'singlecell_app/myseqs.html', context)
    else:
        context['BioUser'] = False
        return render(request, 'singlecell_app/myseqs.html', context)


def MySeqs(request):
    context = {
        'type': 'My Sequences',
        'AllSeq': False
    }
    return render(request, 'singlecell_app/myseqs.html', context)



def MySeqs2(request):
    context = {
        'type': 'My Sequences',
        'AllSeq': False
    }
    return render(request, 'singlecell_app/myseqs2.html', context)

'''
def AllSingleCellData(request):
    """ async function to get hit by ajax. Returns json of all single cell data dict
    in db
    """
    # make sure only bioinformatics group users allowed

    seqs_queryset = SeqInfo.objects.filter(libraryinfo__experiment_type__in=SINGLE_CELL_EXPS).select_related('libraryinfo','libraryinfo__sampleinfo','libraryinfo__sampleinfo__group').order_by(
        '-date_submitted_for_sequencing').values('id', 'seq_id', 'libraryinfo__experiment_type', 'read_type',
                                                 'libraryinfo__sampleinfo__species', 'date_submitted_for_sequencing','libraryinfo__sampleinfo__group','libraryinfo__sampleinfo__sample_id')

    data = list(seqs_queryset)
    build_seq_list(data)
    return JsonResponse(data, safe=False)
'''

def AllSingleCellData(request):
    """ async function to get hit by ajax. Returns json of all single cell data dict
    in db
    """
    # make sure only bioinformatics group users allowed

    seqs_queryset = SingleCellObject.objects.all().select_related('seqinfo',
    'cooladminsubmission','libraryinfo','sampleinfo',
    'seqinfo__libraryinfo__sampleinfo__group').order_by('-date_last_modified').values(
        'seqinfo__id', 'seqinfo__seq_id', 'seqinfo__libraryinfo__experiment_type', 'date_last_modified', 
        'seqinfo__read_type', 'seqinfo__libraryinfo__sampleinfo__species', 
        'seqinfo__libraryinfo__sampleinfo__group','tenx_pipeline_status',
        'seqinfo__libraryinfo__sampleinfo__sample_id','cooladminsubmission__pipeline_status',
        'seqinfo__date_submitted_for_sequencing','cooladminsubmission__link')

    data = list(seqs_queryset)
    build_seq_list_modified(data)

    return JsonResponse(data, safe=False)



def UserSingleCellData(request):
    """async function to get hit by ajax, returns user only seqs
    """
    seqs_queryset = SingleCellObject.objects.filter(seqinfo__team_member_initails=request.user).select_related('seqinfo',
        'cooladminsubmission','libraryinfo','sampleinfo',
        'seqinfo__libraryinfo__sampleinfo__group').order_by('-date_last_modified').values(
        'seqinfo__id', 'seqinfo__seq_id', 'seqinfo__libraryinfo__experiment_type', 'date_last_modified', 
        'seqinfo__read_type', 'seqinfo__libraryinfo__sampleinfo__species', 
        'seqinfo__libraryinfo__sampleinfo__group','tenx_pipeline_status',
        'seqinfo__libraryinfo__sampleinfo__sample_id','cooladminsubmission__pipeline_status',
        'seqinfo__date_submitted_for_sequencing','cooladminsubmission__link')

    data = list(seqs_queryset)
    build_seq_list_modified(data)

    return JsonResponse(data, safe=False)

#TODO Think about when cooladmin being modified and submitted should affect the date of the singlecell seq
def build_seq_list_modified(seqs_list):
    """ This function is used to build seq lists to be returned to the from an 
    AJAX call for AllSeqs2.
    @params
        seqs_list is a list of dictionaires where each has the seq_id and experiment_type for a single cell sample sequence.
    @returns
        returns a list of dictionaries with more information describing the sequence.
        #TODO clean this function up, library IDs not necessary anymore
    """
    # optimize later
    groups = Group.objects.all()
    for entry in seqs_list:
        group_id = entry['seqinfo__libraryinfo__sampleinfo__group']
        group_name = get_group_name(groups, group_id)
        entry['seqinfo__libraryinfo__sampleinfo__group'] = group_name  
        seq_id = entry['seqinfo__seq_id']
        experiment_type = entry['seqinfo__libraryinfo__experiment_type']
        #need to move FASTQ file status to db
        entry['seq_status'] = get_seq_status(seq_id, entry['seqinfo__read_type'])
        entry['species'] = entry['seqinfo__libraryinfo__sampleinfo__species']
        ca_status = entry['cooladminsubmission__pipeline_status']
        entry['cooladmin_status'] = entry['cooladminsubmission__link'] if ca_status == 'Yes' else ca_status

    return (seqs_list)

def build_seq_list(seqs_list):
    """ This function is used to build seq lists to be returned to the from an 
    AJAX call for AllSeqs2.
    @params
        seqs_list is a list of dictionaires where each has the seq_id and experiment_type for a single cell sample sequence.
    @returns
        returns a list of dictionaries with more information describing the sequence.
        #TODO clean this function up, library IDs not necessary anymore
    """
    # optimize later
    cooladmin_objects = CoolAdminSubmission.objects.all()
    groups = Group.objects.all()
    for entry in seqs_list:
        group_id = entry['libraryinfo__sampleinfo__group']
        group_name = get_group_name(groups, group_id)
        entry['libraryinfo__sampleinfo__group'] = group_name        
        seq_id = entry['seq_id']
        experiment_type = entry['libraryinfo__experiment_type']
        entry['last_modified'] = get_latest_modified_time(
            seq_id, entry['id'], entry['date_submitted_for_sequencing'], cooladmin_objects)
        entry['seq_status'] = get_seq_status(seq_id, entry['read_type'])
        entry['10x_status'] = get_tenx_status(seq_id, experiment_type)
        entry['species'] = entry['libraryinfo__sampleinfo__species']
        entry['cooladmin_status'] = get_cooladmin_status(seq_id, entry['id'])
        #entry['group'] = get_group_name(entry)
    return (seqs_list)

def get_group_name(groups, group_id):
    if group_id == None:
        return 'None'
    else:
        return str(groups.get(pk=group_id))

def get_tenx_status(seq, experiment_type):
    """This function returns a string that represents 
    the status of parameter seq in the 10x pipeline.
    @params
        seq: a string that represents the sequence name to be checked.
    @returns
        string 'No' when sequence is not submitted
        string 'InQueue' when sequence is in the qsub queue
        string 'InProcess' when sequence is being processed by 10x pipeline
        string 'Error' when an error occurs in pipeline
        string 'Yes' when the 10x pipeline is succesfully done
    """
    if(experiment_type ==  '10xATAC'):
        dir_to_check = settings.TENX_DIR
    else:
        dir_to_check = settings.SCRNA_DIR

    tenx_output_folder = 'outs'
    tenx_target_outfile = 'web_summary.html'
    path = os.path.join(dir_to_check, str(seq))
    # first check if there is an .inqueue then an .inprocess

    if not os.path.isdir(path):
        seqstatus = 'No'
    elif os.path.isfile(path + '/.inqueue'):
        seqstatus = 'InQueue'
    elif os.path.isfile(path + '/.inprocess'):
        seqstatus = 'InProcess'
    elif os.path.isfile(path + '/outs/_errors'):
        seqstatus = 'Error!'
    else:
        if not os.path.isfile(os.path.join(path,
                                           tenx_output_folder, tenx_target_outfile)):
            seqstatus = 'No'
        elif os.path.isfile(os.path.join(path, tenx_output_folder, tenx_target_outfile)):
            seqstatus = 'Yes'
        else:
            seqstatus = 'No'
    return seqstatus


def get_seq_status(seq_id, read_type):
    """This function checks the FASTQ sequence status and returns the results 
    @params
        seq_id: string represents a seq_id to be checked.
        read_type: Paired end or not
    @returns
        'Yes': FASTQ files present
        'No': no FASTQ files present
    """
    fastqdir = settings.FASTQ_DIR
    #print(f'seq: {seq}, seqid: {seq.seq_id}, readtype: {seq.read_type}')
    reps = seq_id.split('_')[2:]
    mainname = '_'.join(seq_id.split('_')[0:2])
    # reps are [_2] in brandon_210_2 or [_1,_2,_3] in brandon_210_1_2_3
    if len(reps) == 0:
        if read_type == 'PE':
            r1 = mainname + '_R1.fastq.gz'
            r2 = mainname + '_R2.fastq.gz'
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
                    r2 = mainname + '_R2.fastq.gz'
                    if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                        return('No')
                else:
                    r1 = mainname+'.fastq.gz'
                    r1op = mainname+'_R1.fastq.gz'
                    if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                        return('No')
            else:
                # find mainname_rep
                repname = mainname + '_' + rep
                if read_type == 'PE':
                    r1 = repname + '_R1.fastq.gz'
                    r2 = repname + '_R2.fastq.gz'
                    if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                        return ('No')
                else:
                    r1 = repname+'.fastq.gz'
                    r1op = repname+'_R1.fastq.gz'
                    if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                        return ('No')

        # set when for loop statement terminates, all reps fastq's were present
        seqsStatus = 'Yes'
    #print(f'seqstatus: {seqsStatus}')
    return seqsStatus


def get_cooladmin_status(seq_id, seq_pk):
    """
    """
    coolAdminDir = settings.COOLADMIN_DIR

    # requirement: only one active cooladminsubmission object per sequence
    submitted_boolean = CoolAdminSubmission.objects.filter(
        seqinfo=seq_pk, submitted=True).exists()
    # check if folder exists in coolAdminDir
    path = os.path.join(coolAdminDir, seq_id)
    # if no cool admin submitted before or if it has been but the parameters have been changed
    if not os.path.isdir(path) or submitted_boolean == False:
        return 'ClickToSubmit'
    elif os.path.isfile(path + '/.status.processing'):
        return '.status.processing'
    elif os.path.isfile(path + '/.status.success'):
        return get_cooladmin_link(seq_id)
    elif os.path.isfile(path + '/.status.fail'):
        return '.status.fail'
    else:
        return '.status.processing'


def submit_singlecell(request):
    """ This method will be activated when 'clicktosubmit' button is clicked. 
        This method will submit the sequence to be analyzed if the species only has
        one refgenome. If there is more than one refgenome available the the method
        returns the refgenomes availble for user to choose. The user will choose a 
        refgenome and confirm choice and this will be submitted as POST reqeust.
        request: seq - string representing a seq id
        email -string that represents user who submitted job
        POST - ref: string of refgenome chosen
    """
    #GET requests are from initial sc 'clicktosubmit'.  
    if request.method == 'GET':
        seq = request.GET.get('seq')
        if not SeqInfo.objects.filter(seq_id=seq).exists():
            data = {
                'success' : False,
                error: "Seq does not exist!"
            }
        else:
            email = request.user.email
            seq_info = SingleCellObject.objects.select_related(
                'seqinfo__libraryinfo__sampleinfo').values('seqinfo__seq_id',
                'seqinfo__libraryinfo__sampleinfo__species',
                'seqinfo__libraryinfo__experiment_type').get(seqinfo__seq_id=seq)
            print(seq_info)
            species =  seq_info['seqinfo__libraryinfo__sampleinfo__species'].rstrip("\n")
            experiment_type = seq_info['seqinfo__libraryinfo__experiment_type']
            experiment_obj = ExperimentType.objects.get(experiment=experiment_type)
            print('refgenome submission: ',species, experiment_type, experiment_obj)
            #get all refrence genomes available for this experiment type.
            
            refgenomes = RefGenomeInfo.objects.filter(species=species,experiment_type=experiment_obj).values('genome_name')
            refgenome_list = [n['genome_name'] for n in refgenomes]
            print(refgenome_list)
            #submit seqeunce when only one ref genome availalbe, do not prompt user to choose.
            if len(refgenome_list) == 1:
                ref = refgenome_list[0]
                submit_tenX(seq,ref,email)

                data = {
                    'success': True,
                    'submitted' : True,
                }
                return JsonResponse(data)
            elif experiment_type == '10xATAC':
                ref = -1
                submit_tenX(seq,ref,email)

                data = {
                    'success': True,
                    'submitted' : True,
                }
                return JsonResponse(data)
            
            data = {
                'success': True,
                'refs' : refgenome_list,
                'submitted' : False,
            }
        return JsonResponse(data)
    elif request.method == 'POST':
        seq = request.POST.get('seq')
        ref = request.POST.get('ref')
        email = request.user.email

        #run job
        submit_tenX(seq,ref,email)

        data = {
            'success' : True,
        }
        return JsonResponse(data)



# TODO add a modify_submission_model() funciton to update submission date_submitted/modified and submitted fields


def submit_cooladmin(request):
    """This function handles a cooladmin submission request from LIMS user.
    This function run a bash script ./utility/coolAdmin.sh
    """
    seq = request.POST.get('seq')
    email = request.user.email
    info = SeqInfo.objects.select_related(
        'libraryinfo__sampleinfo').get(seq_id=seq)
    species = defaultgenome[info.libraryinfo.sampleinfo.species.lower()]

    defaults = {
        'submitted': True,
        'seqinfo': info,
        'date_submitted': datetime.now(),
        'date_modified': datetime.now(),
    }

    submission, created = CoolAdminSubmission.objects.update_or_create(seqinfo=info,
                                                                       defaults=defaults)
    submission_dict = model_to_dict(submission)
    if created == True:
        if(info.libraryinfo.sampleinfo.experiment_type_choice == '10xATAC'):
            submission_dict['refgenome'] = getReferenceUsed(seq)
        else:  # set ref genome to default species
            submission_dict['refgenome'] = species
            submission.date_modified = datetime.now()
    else:
        #print('submission dict: ', submission_dict)
        if(info.libraryinfo.sampleinfo.experiment_type_choice == '10xATAC'):
            submission_dict['refgenome'] = getReferenceUsed(seq)
    
    submission.date_submitted = datetime.now() 
    submission.pipeline_status = INQUEUE
    submission.submitted = True
    submission.save()

    
    seqString = f'"{seq}"'

    paramString = buildCoolAdminParameterString(
        submission_dict).replace('"', '\\"').replace(' ', '\\ ')
    #print('paramString: ', paramString)
    cmd1 = f'bash ./utility/coolAdmin.sh {email} {seqString} {paramString}'
    #print(cmd1)

    p = subprocess.Popen(
        cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data = {
        'is_submitted': True
    }
    return JsonResponse(data, safe=False)


# TODO write test for this function
# TODO handle repsonse when edit is invalid
def edit_cooladmin_sub(request, seqinfo):
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
    seqinfo_id = get_object_or_404(SeqInfo, seq_id=seqinfo)
    #print('edit reqeust: ',(request.user.groups.filter(name='bioinformatics').exists()))
    if(not request.user.groups.filter(name='bioinformatics').exists() and request.user != seqinfo_id.team_member_initails):
        print('raising exception')
        raise PermissionDenied

    seqinfo = SeqInfo.objects.select_related(
        'libraryinfo__sampleinfo').get(seq_id=seqinfo_id)
    species = seqinfo.libraryinfo.sampleinfo.species
    exptType = seqinfo.libraryinfo.experiment_type

    # starter_data for initialization values of CoolAdminSubmissionForm
    starter_data = {
        'species': species,
        'seqinfo': seqinfo,
    }

    ref_genome_used = ""
    submission = False

    # get previous cool admin submission if exists
    if CoolAdminSubmission.objects.filter(seqinfo=seqinfo_id).exists():
        submission = CoolAdminSubmission.objects.get(seqinfo=seqinfo_id)
        # make form based on model values
        form = CoolAdminForm(initial=model_to_dict(submission), spec=species)
        # set the choice field based on the key of the tuple using the previous submission
        if(exptType == '10xATAC'):  # set ref genome if 10xATAC type of experiment
            ref_genome_used = getReferenceUsed(seqinfo)
            form.fields['refgenome'].initial = [ref_genome_used]
        else:
            form.fields['refgenome'].initial = [submission.refgenome]
    else:  # create a form with starter data if no previous submission form
        form = CoolAdminForm(initial=starter_data, spec=species)
        if(exptType == '10xATAC'):
            ref_genome_used = getReferenceUsed(seqinfo)
            form.fields['refgenome'].initial = [ref_genome_used]
        else:
            form.fields['refgenome'].initial = [defaultgenome[species]]

    # handle save of new submission form
    if request.method == 'POST':
        post = request.POST.copy()
        post['seqinfo'] = seqinfo_id

        # overwrite refgenome to post data
        if(exptType == '10xATAC'):
            post['refgenome'] = ref_genome_used

        # if previous submission, compare to new submission
        if(submission != False):
            data = model_to_dict(submission)
            data['genome'] = data['refgenome']
            #print('\n data: ',data)
            #print('\n post: ',post)
            form = CoolAdminForm(post, initial=data)
            #print('form: is valid and has changed: ',form.is_valid(), form.has_changed())
            if form.is_valid():
                if(form.has_changed()):
                    data = form.cleaned_data
                    data['submitted'] = False
                    #print('changed data: ', form.changed_data)
                    CoolAdminSubmission.objects.filter(
                        seqinfo=seqinfo_id).update(**data)
                    obj = CoolAdminSubmission.objects.get(seqinfo=seqinfo_id)
                    obj.date_modified = datetime.now()
                    obj.save()
                else:
                    print('no changes to submission!')
            else:
                print('form not valid!')
        else:
            # there was no previous submission but new data was posted: save these parameters if they are different from the defaults
            form = CoolAdminForm(post)
            if form.is_valid():
                data = form.cleaned_data
                data['seqinfo'] = seqinfo_id
                obj = CoolAdminSubmission(**data)
                obj.save()
                #print('new submission: ',model_to_dict(obj))

        return redirect('singlecell_app:myseqs')

    context = {
        'form': form,
        'seq': seqinfo,
    }
    return render(request, 'singlecell_app/editCoolAdmin.html', context)


def get_cooladmin_link(seq):
    """Call this function when cooladmin status has already been confirmed to be success
    """
    #cool_dir = f'/projects/ps-epigen/datasets/opoirion/output_LIMS/{seq}/repl1//repl1_{seq}_finals_logs.json'
    cool_dir = settings.COOLADMIN_DIR
    try:
        json_file = os.path.join(
            cool_dir, seq, 'repl1', 'repl1_' + seq + '_final_logs.json')
        with open(json_file, 'r') as f:
            cool_data = f.read()
        cool_dict = json.loads(cool_data)
        #print('cooldict: ', cool_dict)
        return (cool_dict['report_address'])
    except:
        return("")


def setup_submission(seq_object, data):
    """This helper function will assign values to the data dict based on the 
    experimental type and species/genome of the seq object. Will return the data dict so that the
    submission funtion can use the dict for bash script parameters.
    """
    
    return data


def submit_tenX(seq, refgenome, email):
    """ This function should only be called by another fucntion that ensures the sequence is valid to be submitted
    This function submits a sequence to 10x cell ranger or 10x atac pipeline
    """
    
    seq_info = list(SeqInfo.objects.filter(seq_id=seq).select_related(
        'libraryinfo__sampleinfo').values('seq_id',
        'libraryinfo__sampleinfo__species','read_type',
        'libraryinfo__experiment_type'))
    data = {}
    data['seqs'] = split_seqs(seq_info[0]['seq_id'])
    data['species'] =  seq_info[0]['libraryinfo__sampleinfo__species'].rstrip("\n")
     
    experiment_type = seq_info[0]['libraryinfo__experiment_type']
    #get all refrence genomes available for this experiment type.
    
    
    #print('refgenomes present: ', str(refgenome))
    
    #set output dir based on experiment type
    if experiment_type == '10xATAC':
        dir = settings.TENX_DIR
        #set genome that run10xPipeline.pbs will use
        data['genome'] = 'mm10' if data['species'].lower() == 'mouse' else 'hg38'

    else:
        dir = settings.SCRNA_DIR
        refgenome = RefGenomeInfo.objects.get(species=data['species'],genome_name=refgenome,experiment_type__experiment=experiment_type)
        data['genome'] = str(refgenome)
        data['ref_path'] = refgenome.path

    #write tsv samplesheet: filename = ".sequence.tsv"
    filename = '.'+str(seq)+'.tsv'
    tsv_writecontent = '\t'.join([seq, ','.join(data['seqs']), data['genome']]) 
    seqDir = os.path.join(dir, seq)
   
    #replace with db update that this seq status is inqueue
    if not os.path.exists(seqDir):
        os.mkdir(seqDir)
    inqueue = os.path.join(seqDir, '.inqueue')
    with open(inqueue, 'w') as f:
        f.write('')
    tsv_file = os.path.join(seqDir, filename)
    with open(tsv_file, 'w') as f:
        f.write(tsv_writecontent+'\n')
        
    #set command depedning on experiment

    if( experiment_type == '10xATAC'):
        cmd1 = 'bash ./utility/run10xOnly.sh %s %s %s' %(seq, dir, email)
    else:
        cmd1 = ('bash ./utility/runCellRanger.sh %s %s %s %s' %(seq,
         data['ref_path'], dir, email))

    print('cmd submitted: ',cmd1)
    p = subprocess.Popen(
        cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    #update singlecellobject db entry that seq is inq
    sc_obj = SingleCellObject.objects.get(seqinfo__seq_id=seq)
    sc_obj.tenx_pipeline_status = INQUEUE
    sc_obj.date_last_modified = datetime.now()
    sc_obj.save()
    return True


def split_seqs(seq):
    splt = seq.split('_')
    addlseqs = []
    basename = ('_').join(splt[:2])
    if len(splt) < 3:
        # do nothing special
        return [basename]
    else:
        for addlseq in splt[2:]:
            if addlseq == '1':
                addlseqs.append(basename)
            else:
                addlseqs.append(basename+'_'+addlseq)
    return addlseqs

# TODO do param error checking?
def buildCoolAdminParameterString(dict):
    #print('dict: ', dict)
    paramString = ''
    for key in SNAP_PARAM_DICT.keys():
        paramString += f'{SNAP_PARAM_DICT[key]}="{dict[key]}",'
    return paramString


def getReferenceUsed(seq):
    """This function gets the ref genome used in 10x atac pipeline to use for cool admin submission
    @params seq is a string of the sequnece wanted e.g. seq="JYH_1047"
    @returns a string that is the refernce genome used
    """

    # To return
    refgenome = 'N/A'

    tenx_output_folder = 'outs'
    tenx_target_outfile = 'summary.json'
    tenxdir = settings.TENX_DIR

    file_path = os.path.join(tenxdir, str(
        seq), tenx_output_folder, tenx_target_outfile)
    if(os.path.exists(file_path)):
        with open(file_path) as json_file:
            data = json.load(json_file)
            refgenome = data["reference_assembly"]
    # open summarry.json and read "reference_assembly"
    return refgenome


def get_latest_modified_time(seq_id, seq_object_id, date_sub_for_seq, cooladmin_objects):
    """
    This function returns the latest modfication to the seq object
    """
    # first get time that seqinfo object was submitted for sequencing - this will always exist
    time = date_sub_for_seq
    #print('time: ',time)

    # check if user modified cooladmin submission params, check if user submitted either cooladmin OR 10xCellranger job
    # check if cooladminsubmission exists
    cooladmin_time_check = check_cooladmin_time(
        seq_object_id, cooladmin_objects)
    if(time == None and cooladmin_time_check != None):
        time = cooladmin_time_check
    elif(time != None and cooladmin_time_check != None and time < cooladmin_time_check):
        time = cooladmin_time_check
    #print('cooladmin_time_check: ', cooladmin_time_check)

    # check if sequencestatus has updated? pipeline status's updates?
    tenx_time_check = check_tenx_time(seq_id)
    if(time == None and tenx_time_check != None):
        time = tenx_time_check
    elif(time != None and tenx_time_check != None and time < tenx_time_check):
        time = tenx_time_check
    return time


def check_cooladmin_time(seq_object_id, cooladmin_objects):
    if cooladmin_objects.filter(seqinfo=seq_object_id).exists():
        cooladmin_object = cooladmin_objects.get(seqinfo=seq_object_id)
        date_submitted = cooladmin_object.date_submitted
        date_modified = cooladmin_object.date_modified
        #print('ca object: ',date_modified, date_submitted)
        if(date_submitted == None):
            time = date_modified
        # date_modified never == None, if cooladmin sub object exists - it must have been modified at time of creation
        elif(date_modified == None):
            time = date_submitted
        elif(date_modified < date_submitted):
            time = date_submitted
        else:
            time = date_modified
        return time.date()
    else:
        return None


def check_tenx_time(seq_id):
    # check if tenx dir exists for seq_id
    tenxdir = settings.TENX_DIR
    # first check if there is an .inqueue then an .inprocess
    path = os.path.join(tenxdir, str(seq_id))
    if(os.path.isdir(path) == True):
        last_mod_time = os.path.getmtime(path)
        time = datetime.fromtimestamp(last_mod_time).date()
    else:
        time = None
    #print('tenx time: ',time)
    # convert time to datetime
    return(time)


def generate_tenx_link(request):
    """ return a link for files to be viewed with a share link
    Will generate a link if needed. Will return the link in the response.
    """
    print(request)
    LENGTH_OF_KEY = 9  # put this in the deploy or settings file?
    seq = request.GET.get('seq')
    #print('genertaing link for seq: ', seq)
    info = {}
    data = {}
    try:
        seq_object = SeqInfo.objects.select_related(
            'libraryinfo').get(seq_id=seq)
    except ObjectDoesNotExist:
        print('SeqObject does not exist!')
        data['error'] = "Sequence object does not exist!"
        return JsonResponse(data, safe=False)

    # get seq owner:
    library_info = seq_object.libraryinfo
    info['experiment_type'] = library_info.experiment_type
    info['seq_owner'] = seq_object.team_member_initails
    info['seq_id'] = seq_object.seq_id
    #print(info)
    #print(request.user)
    if request.user.groups.filter(name='bioinformatics').exists() or info['seq_owner'] == request.user:
        # get all files in exposed outs folder
        exposed_outs_dir = settings.EXPOSED_OUTS_DIR
        listdir = os.listdir(exposed_outs_dir)
        basenames = [os.path.basename(fn)[LENGTH_OF_KEY:] for fn in listdir]
        filenames_dict = {}
        for i in range(len(listdir)):
            filenames_dict[basenames[i]] = listdir[i]

        # get directory that seq is in
        # check if symbolic link is present
        if(seq not in (basenames)):
            # Do symbolic linking
            if info['experiment_type'] == '10xATAC':
                parent_dir = settings.TENX_DIR
            else:
                parent_dir = settings.SCRNA_DIR
            output_dir = 'outs'
            to_link_dir = os.path.join(parent_dir, info['seq_id'], output_dir)

            # create link name
            chars = (string.ascii_uppercase +
                     string.digits + string.ascii_lowercase)
            link = ''.join(random.choice(chars)
                           for x in range(LENGTH_OF_KEY - 1))
            link += '_' + seq
            fullpath_link = os.path.join(settings.EXPOSED_OUTS_DIR, link)

            link = os.path.join(os.path.basename(
                os.path.split(exposed_outs_dir)[0]), link)
            os.system("ln -s %s %s" % (to_link_dir, fullpath_link))
            # bash script process

        else:
            link = filenames_dict[seq]
            link = os.path.join(os.path.basename(
                os.path.split(exposed_outs_dir)[0]), link)
        
        data['link'] = link
        return JsonResponse(data, safe= False)
    else:
        data["error"] = "Permission denied"
        return JsonResponse(data,safe=False)
      

#TODO check where generate link is called, ensure expt_type is passed in
def generate_link(seq, expt_type):
    """ return a link for files to be viewed with a share link
    Will generate a link if needed. Will return the link in the response.
    """
    LENGTH_OF_KEY = 9  # put this in the deploy or settings file?
    #print('genertaing link for seq: ', seq)
    info = {}
    data = {}
    parent_dir = ""
    
    # get all files in exposed outs folder
    exposed_outs_dir = settings.EXPOSED_OUTS_DIR
    listdir = os.listdir(exposed_outs_dir)
    basenames = [os.path.basename(fn)[LENGTH_OF_KEY:] for fn in listdir]
    filenames_dict = {}
    for i in range(len(listdir)):
        filenames_dict[basenames[i]] = listdir[i]

    # get directory that seq is in
    # check if symbolic link is present
    if(seq not in (basenames)):
        # Do symbolic linking
        parent_dir = settings.TENX_DIR if expt_type == "10xATAC" else settings.SCRNA_DIR
        output_dir = 'outs'
        to_link_dir = os.path.join(parent_dir, seq, output_dir)

        # create link name
        chars = (string.ascii_uppercase +
                 string.digits + string.ascii_lowercase)
        link = ''.join(random.choice(chars)
                       for x in range(LENGTH_OF_KEY - 1))
        link += '_' + seq
        fullpath_link = os.path.join(settings.EXPOSED_OUTS_DIR, link)

        link = os.path.join(os.path.basename(
            os.path.split(exposed_outs_dir)[0]), link)
        os.system("ln -s %s %s" % (to_link_dir, fullpath_link))
        # bash script process

    else:
        link = filenames_dict[seq]
        print(link)
        link = os.path.join(os.path.basename(
            os.path.split(exposed_outs_dir)[0]), link)
        print(link)
    url = 'http://epigenomics.sdsc.edu/zhc268/' + link

    return(url)


def insert_link(filename, seq, expt_type):
    """ Insert link into header of the web_summary.html
        for scRNA experiments, insert at line 1430.
    """
    #magic numbers, where we will insert link in web_summary.html
    TENXATAC_LINE = 10
    SCRNA_LINE = 1430
    line_to_insert_at = TENXATAC_LINE if expt_type == '10xATAC' else SCRNA_LINE
    newdata = "" # will hold the old html + an inserted link at specified line
    link = generate_link(seq, expt_type) #generate a link to the output folder
    if(link == -1):
        print('error in generate_link!')
        return
    file_open = open(filename)
    f1 = file_open.readlines()
    for num, line in enumerate(f1, start=1):
        if num == line_to_insert_at:
            newdata = newdata + '<div><h2><a class="data-link-epigen" style="margin-left:3em;" href="'+link+'"> Link to Output Data</a></h2><div>'
        newdata = newdata + line
    file_open.close()
    #may be too much data in memory
    with open(filename, 'w') as overwrite:
        overwrite.write(newdata)


def view_websummary(request, seq_id):
    '''
    This function opens and returns html webpage created by 10x pipelines for singlecell app
    @Requirements: the 10x webpage requested is softlinked in the BASE_DIR/data/websummary 
    directory, where BASE_DIR is either settings.TENX_DIR or settings.SCRNA_DIR.
    '''
    user = request.user
    seqinfo = SeqInfo.objects.select_related('libraryinfo','libraryinfo__sampleinfo','libraryinfo__sampleinfo__group').get(seq_id=seq_id)
    permission = check_permissions(user=user, seqinfo=seqinfo)

    if permission == False:
        print('Access is denied to seq {seq_id} for user {user}'.format(seq_id=seq_id,user=user))
        raise PermissionDenied
    
    dir = ""
    print(seqinfo)
    expt_type = seqinfo.libraryinfo.experiment_type
    if(expt_type == '10xATAC'):
        dir = settings.TENX_DIR
    else:
        dir = settings.SCRNA_DIR

    path = '{dir}/{seq_id}/outs/web_summary.html'.format(seq_id=seq_id,dir=dir)
    print('reading: ',path)
    file = open(path)
    data = file.read()
    if(LINK_CLASS_NAME not in data):
        #print('in tenxoutput2() for singlecell, adding link to file')
        file.close()
        insert_link(path, seq_id, expt_type)
        file=open(path)
        data = file.read()
    if(data == None):
        print('ERROR: No data read in 10x Web_Summary.html File! for {seq_id}'.format(seq_id=seq_id) )
    return HttpResponse(data)


def check_permissions(seqinfo, user):
    """ If user is staff or bioinformatics let them view, if the user is 
    collaborator then they must be part of the group. Return True if permission
    is granted.bi
    """
    #get group that seq is assigned to
    seq_group = seqinfo.libraryinfo.sampleinfo.group
    #check if user is staff,bioinformatics, or in seq_group
    
    return True if is_in_multiple_groups(user, ['bioinformatics','staff','wetlab',seq_group]) else False

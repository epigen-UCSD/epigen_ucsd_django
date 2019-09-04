from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SampleCreationForm, LibraryCreationForm, SeqCreationForm,\
    SamplesCreationForm, LibsCreationForm, SeqsCreationForm, SeqsCreationForm,\
    LibsCreationForm_wetlab,SeqsCreationForm_wetlab,BulkUpdateForm
from .models import SampleInfo, LibraryInfo, SeqInfo, ProtocalInfo, \
    SeqMachineInfo, SeqBioInfo, choice_for_preparation, choice_for_fixation,\
    choice_for_unit, choice_for_sample_type
from django.contrib.auth.models import User, Group
from nextseq_app.models import Barcode
from epigen_ucsd_django.shared import datetransform
from django.http import HttpResponse,JsonResponse
from django.db.models import Q
from epigen_ucsd_django.models import CollaboratorPersonInfo
import xlwt
from django.db.models import Prefetch
import re
import secrets,string
from random import randint
from django.conf import settings
import os

def nonetolist(inputthing):
    if not inputthing:
        return []
    else:
        return inputthing

def removenone(inputlist):
    #remove None and duplicate value in inputlist, e.g. ['fe',None,'','gg'] to ['fe','gg']
    if not inputlist:
        return []
    else:
        y = [x for x in inputlist if x]
        return list(sorted(set(y),key=y.index))
# Create your views here.
# @transaction.atomic
# def SampleCreateView(request):
#     sample_form = SampleCreationForm(request.POST or None)
#     if sample_form.is_valid():
#         sampleinfo = sample_form.save(commit=False)
#         sampleinfo.team_member = request.user
#         sampleindexs = list(SampleInfo.objects.values_list('sample_index', flat=True))
#         if not sampleindexs:
#             sampleinfo.sample_index = 'SAMP-2000'
#         else:
#             maxid = max([int(x.split('-')[1]) for x in sampleindexs if x.startswith('SAMP-')])
#             sampleinfo.sample_index = '-'.join(['SAMP',str(maxid+1)])
#         sampleinfo.save()
#         return redirect('masterseq_app:index')
#     context = {
#         'sample_form': sample_form,
#     }


#     return render(request, 'masterseq_app/sampleadd.html', context)

# @transaction.atomic
# def LibraryCreateView(request):
#     library_form = LibraryCreationForm(request.POST or None)
#     if library_form.is_valid():
#         librayinfo = library_form.save(commit=False)
#         librayinfo.team_member_initails = request.user
#         expindexs = list(LibraryInfo.objects.values_list('experiment_index', flat=True))
#         if not expindexs:
#             librayinfo.experiment_index = 'EXP-2000'
#         else:
#             maxid = max([int(x.split('-')[1]) for x in expindexs if x.startswith('EXP-')])
#             librayinfo.experiment_index = '-'.join(['EXP',str(maxid+1)])
#         librayinfo.save()
#         return redirect('masterseq_app:index')
#     context = {
#         'library_form': library_form,
#     }
#     return render(request, 'masterseq_app/libraryadd.html', context)

# @transaction.atomic
# def SeqCreateView(request):
#     seq_form = SeqCreationForm(request.POST or None)
#     tosave_list = []
#     if seq_form.is_valid():
#         readlen = seq_form.cleaned_data['read_length']
#         machine = seq_form.cleaned_data['machine']
#         readtype = seq_form.cleaned_data['read_type']
#         date = seq_form.cleaned_data['date_submitted_for_sequencing']
#         sequencinginfo = seq_form.cleaned_data['sequencinginfo']
#         #print(sequencinginfo)
#         for lineitem in sequencinginfo.strip().split('\n'):
#             if not lineitem.startswith('SeqID\tLibID') and lineitem != '\r':
#                 lineitem = lineitem+'\t\t\t\t\t\t'
#                 fields = lineitem.strip('\n').split('\t')
#                 seqid = fields[0]
#                 print(seqid)
#                 libid = LibraryInfo.objects.get(library_id=fields[1])
#                 dflabel = fields[2]
#                 tmem = User.objects.get(username=fields[3])
#                 if fields[4]:
#                     polane = float(fields[4])
#                 else:
#                     polane = None
#                 if fields[5]:
#                     i7index = Barcode.objects.get(indexid=fields[5])
#                 else:
#                     i7index = None
#                 if fields[6]:
#                     i5index = Barcode.objects.get(indexid=fields[5])
#                 else:
#                     i5index = None
#                 if fields[7]:
#                     notes = fields[7]
#                 else:
#                     notes = ''
#                 tosave_item = SeqInfo(
#                     seq_id = seqid,
#                     libraryinfo = libid,
#                     team_member_initails = tmem,
#                     machine = machine,
#                     read_length = readlen,
#                     read_type = readtype,
#                     portion_of_lane = polane,
#                     i7index = i7index,
#                     i5index = i5index,
#                     date_submitted_for_sequencing = date,
#                     default_label = dflabel,
#                     notes = notes
#                     )
#                 tosave_list.append(tosave_item)
#         SeqInfo.objects.bulk_create(tosave_list)
#         return redirect('masterseq_app:index')
#     context = {
#         'seq_form': seq_form,
#     }


#     return render(request, 'masterseq_app/seqadd.html', context)


def load_protocals(request):
    exptype = request.GET.get('exptype')
    protocals = ProtocalInfo.objects.filter(
        experiment_type=exptype).order_by('protocal_name')
    print(protocals)
    return render(request, 'masterseq_app/protocal_dropdown_list_options.html', {'protocals': protocals})

def BulkUpdateView(request):
    update_form = BulkUpdateForm(request.POST or None)
    context = {
        'update_form': update_form,
    }

    return render(request, 'masterseq_app/bulkupdate.html', context)



@transaction.atomic
def SamplesCreateView(request):
    sample_form = SamplesCreationForm(request.POST or None)
    tosave_list = []
    data = {}
    newuserrequired = 0
    newinforequired = 0
    alreadynewuser = []
    if sample_form.is_valid():
        sampleinfo = sample_form.cleaned_data['samplesinfo']
        all_index = list(SampleInfo.objects.values_list('sample_index', flat=True))
        max_index = max([int(x.split('-')[1]) for x in all_index if x.startswith('SAMP-') and '&' not in x])
        for lineitem in sampleinfo.strip().split('\n'):
            lineitem = lineitem+'\t'*20
            fields = lineitem.strip('\n').split('\t')
            samindex = 'SAMP-'+str(max_index +1)
            max_index = max_index +1            
            newresuserflag = 0
            newresinfoflag = 0
            user_first_name = ''
            user_last_name = ''
            user_username = '',
            user_email = '',
            user_phone = '',
            user_index = '',
            new_email = ''
            new_phone ='' 
            new_index = ''     
            newfisuserflag = 0
            newfisinfoflag = 0
            fisuser_first_name = ''
            fisuser_last_name = ''
            fisuser_username = '',
            fisuser_email = '',
            fisuser_phone = '',
            fisuser_index = '',
            fisnew_email = ''
            fisnew_phone ='' 
            fisnew_index = '' 
            gname = fields[1].strip() if fields[1].strip() not in ['NA','N/A'] else ''
            resname = fields[2].strip() if fields[2].strip() not in ['NA','N/A'] else ''
            resemail = fields[3].strip().lower() if fields[3].strip() not in ['NA','N/A'] else ''
            resphone = re.sub('-| |\.|\(|\)|ext', '', fields[4].strip()) if fields[4].strip() not in ['NA','N/A'] else ''
            if resemail:
                thisgroup = Group.objects.get(name=gname)
                if thisgroup.collaboratorpersoninfo_set.all().filter(email__contains=[resemail]).exists():
                    resperson = thisgroup.collaboratorpersoninfo_set.all().get(email__contains=[resemail])
                    resname = resperson.person_id.first_name+' '+resperson.person_id.last_name
                    user_first_name = resname.split(' ')[0]
                    user_last_name = resname.split(' ')[-1]
                    if resphone:
                        if resphone not in resperson.phone:
                            newinforequired = 1
                            newresinfoflag = 1
                            new_phone = resphone                    
                
                else:
                    user_first_name = resname.split(' ')[0]
                    user_last_name = resname.split(' ')[-1]
                    try:
                        resuser = User.objects.filter(groups__name__in=[gname]).get(first_name=resname.split(' ')[0],last_name=resname.split(' ')[-1])
                        resperson,created = CollaboratorPersonInfo.objects.get_or_create(person_id=resuser,group=thisgroup)
                        newinforequired = 1
                        newresinfoflag = 1
                        new_email = resemail
                        if resphone:
                            if resphone not in resperson.phone:
                                new_phone = resphone

                    except:
                        newuserrequired = 1                       
                        if user_first_name+' '+user_last_name not in alreadynewuser:
                            alreadynewuser.append(user_first_name+' '+user_last_name)
                            newresuserflag = 1
                            user_username = user_first_name[0].lower()+user_last_name.lower()
                            if User.objects.filter(username=user_username).exists():
                                user_username = user_first_name[0]+str(randint(0, 9))+user_last_name.lower()


            elif resname:
                user_first_name = resname.split(' ')[0]
                user_last_name = resname.split(' ')[-1]
                try:
                    resuser = User.objects.filter(groups__name__in=[gname]).get(first_name=resname.split(' ')[0],last_name=resname.split(' ')[-1])
                    resperson,created = CollaboratorPersonInfo.objects.get_or_create(person_id=resuser,group=thisgroup)
                    newinforequired = 1
                    newresinfoflag = 1
                    new_email = ''
                    if resphone:
                        if resphone not in resperson.phone:
                            new_phone = resphone
                except:
                    newuserrequired = 1
                    if user_first_name+' '+user_last_name not in alreadynewuser:
                        alreadynewuser.append(user_first_name+' '+user_last_name)
                        newresuserflag = 1
                        user_username = user_first_name[0].lower()+user_last_name.lower()
                        if User.objects.filter(username=user_username).exists():
                            user_username = user_first_name[0]+str(randint(0, 9))+user_last_name.lower()                                    

            fisname = fields[5].strip() if fields[5].strip() not in ['NA','N/A'] else ''
            fisemail = fields[6].strip().lower() if fields[6].strip() not in ['NA','N/A'] else ''
            indname = fields[7].strip() if fields[7].strip() not in ['NA','N/A'] else ''
            if fisemail:
                thisgroup = Group.objects.get(name=gname)
                if thisgroup.collaboratorpersoninfo_set.all().filter(email__contains=[fisemail]).exists():
                    fisperson = thisgroup.collaboratorpersoninfo_set.all().get(email__contains=[fisemail])
                    fisname = fisperson.person_id.first_name+' '+fisperson.person_id.last_name
                    fisuser_first_name = fisname.split(' ')[0]
                    fisuser_last_name = fisname.split(' ')[-1]
                    if indname:
                        if indname not in fisperson.index:
                            newinforequired = 1
                            newfisinfoflag = 1
                            fisnew_index = indname  

                else:
                    fisuser_first_name = fisname.split(' ')[0]
                    fisuser_last_name = fisname.split(' ')[-1]
                    try:
                        fisuser = User.objects.filter(groups__name__in=[gname]).get(first_name=fisname.split(' ')[0],last_name=fisname.split(' ')[-1])
                        fisperson,created = CollaboratorPersonInfo.objects.get_or_create(person_id=fisuser,group=thisgroup)
                        newinforequired = 1
                        newfisinfoflag = 1
                        fisnew_email = fisemail
                        if indname:
                            if indname not in fisperson.index:
                                fisnew_index = indname 

                    except:
                        newuserrequired = 1
                        if fisuser_first_name+' '+fisuser_last_name not in alreadynewuser:
                            alreadynewuser.append(fisuser_first_name+' '+fisuser_last_name)
                            newfisuserflag = 1
                            fisuser_username = fisuser_first_name[0].lower()+fisuser_last_name.lower()
                            if User.objects.filter(username=fisuser_username).exists():
                                fisuser_username = fisuser_first_name[0]+str(randint(0, 9))+fisuser_last_name.lower() 

            elif fisname:
                fisuser_first_name = fisname.split(' ')[0]
                fisuser_last_name = fisname.split(' ')[-1]
                try:
                    fisuser = User.objects.filter(groups__name__in=[gname]).get(first_name=fisname.split(' ')[0],last_name=fisname.split(' ')[-1])
                    fisperson,created = CollaboratorPersonInfo.objects.get_or_create(person_id=fisuser,group=thisgroup)
                    newinforequired = 1
                    newfisinfoflag = 1
                    fisnew_email = ''
                    if indname:
                        if indname not in fisperson.index:
                            fisnew_index = indname 
                except:
                    newuserrequired = 1
                    if fisuser_first_name+' '+fisuser_last_name not in alreadynewuser:
                        alreadynewuser.append(fisuser_first_name+' '+fisuser_last_name)
                        newfisuserflag = 1
                        fisuser_username = fisuser_first_name[0].lower()+fisuser_last_name.lower()
                        if User.objects.filter(username=fisuser_username).exists():
                            fisuser_username = fisuser_first_name[0]+str(randint(0, 9))+fisuser_last_name.lower()                                    


            samnotes = fields[20].strip()
            try:
                saminternalnotes = fields[24].strip()
            except:
                saminternalnotes = ''
            try:
                membername = fields[22].strip()
                if membername == '':
                    membername = request.user.username
            except:
                membername = request.user.username
            try:
                storage_tm = fields[23].strip()
            except:
                storage_tm = ''
            service_requested_tm = fields[16].strip()
            seq_depth_to_target_tm = fields[17].strip()
            seq_length_requested_tm = fields[18].strip()
            seq_type_requested_tm = fields[19].strip()
            samprep = fields[12].strip().lower().replace(
                'crypreserant', 'cryopreservant')
            if samprep not in [x[0].split('(')[0].strip() for x in choice_for_preparation]:
                if samprep.lower().startswith('other'):
                    samprep = 'other (please explain in notes)'
                else:
                    if samprep:
                        samnotes = ';'.join(
                            [samnotes, 'sample preparation:'+samprep]).strip(';')
                    samprep = 'other (please explain in notes)'
            samtype = fields[11].split('(')[0].strip().lower()
            samspecies = fields[10].split('(')[0].lower().strip()
            unit = fields[15].split('(')[0].strip().lower()
            fixation = fields[13].strip().lower()
            if fixation == 'yes (1% fa)':
                fixation = 'Yes (1% FA)'
            elif fixation == 'no':
                fixation = 'No'
            if service_requested_tm.lower().startswith('other'):
                service_requested_tm = 'other (please explain in notes)'
            sample_amount = fields[14].strip()
            samdescript = fields[9].strip()
            samid = fields[8].strip()
            samdate = datetransform(fields[0].strip())
            try:
                date_received = datetransform(fields[21].strip())
            except:
                date_received = None
            data[samid] = {}
            data[samid] = {
                'sample_index': samindex,
                'group':gname,
                'research_name':resname, 
                'research_email':resemail,
                'research_phone':resphone,
                'user_index':'',
                'fiscal_name':fisname, 
                'fiscal_email':fisemail,
                'fiscal_phone':'',
                'fiscal_index':indname,
                'team_member': membername,
                'date': samdate,
                'date_received': date_received,
                'species': samspecies,
                'sample_type': samtype,
                'preparation': samprep,
                'fixation': fixation,
                'sample_amount': sample_amount,
                'unit': unit,
                'description': samdescript,
                'storage': storage_tm,
                'notes': samnotes,
                'internal_notes':saminternalnotes,
                'service_requested':service_requested_tm,
                'seq_depth_to_target':seq_depth_to_target_tm,
                'seq_length_requested':seq_length_requested_tm,
                'seq_type_requested':seq_type_requested_tm,
                'newresuserflag':newresuserflag,
                'newresinfoflag':newresinfoflag,
                'newfisuserflag':newfisuserflag,
                'newfisinfoflag':newfisinfoflag,
                'user_first_name':user_first_name,
                'user_last_name':user_last_name,
                'user_username':user_username,
                'user_email':resemail,
                'user_phone':resphone,
                'user_index':'',
                'new_email':new_email,
                'new_phone':new_phone,
                'new_index':new_index,
                'fisuser_first_name':fisuser_first_name,
                'fisuser_last_name':fisuser_last_name,
                'fisuser_username':fisuser_username,
                'fisuser_email':fisemail,
                'fisuser_phone':'',
                'fisuser_index':indname,
                'fisnew_email':fisnew_email,
                'fisnew_phone':fisnew_phone,
                'fisnew_index':fisnew_index,               
            }

        if 'Save' in request.POST:
            for k,v in data.items():
                if v['group']:
                    group_tm = Group.objects.get(name=v['group'])
                else:
                    group_tm = None
                if v['newresuserflag']==1:
                    alphabet = string.ascii_letters + string.digits
                    passwordrand = ''.join(secrets.choice(alphabet) for i in range(10))
                    resaccount = User.objects.create_user(
                        username = v['user_username'],
                        first_name = v['user_first_name'],
                        last_name = v['user_last_name'],
                        password = passwordrand,
                        )
                    group_tm.user_set.add(resaccount)
                    resperson = CollaboratorPersonInfo.objects.create(
                        person_id=resaccount,
                        group=group_tm,
                        email=removenone([v['research_email']]),
                        phone=removenone([v['research_phone']]),
                        )
                if v['newfisuserflag']==1:
                    alphabet = string.ascii_letters + string.digits
                    passwordrand = ''.join(secrets.choice(alphabet) for i in range(10))
                    fisaccount = User.objects.create_user(
                        username = v['fisuser_username'],
                        first_name = v['fisuser_first_name'],
                        last_name = v['fisuser_last_name'],
                        password = passwordrand,
                        )
                    group_tm.user_set.add(fisaccount)
                    fisperson = CollaboratorPersonInfo.objects.create(
                        person_id=fisaccount,
                        group=group_tm,
                        email=removenone([v['fiscal_email']]),
                        index=removenone([v['fiscal_index']]),
                        )
                if v['newresinfoflag']==1:
                    resuser = User.objects.filter(groups__name__in=[v['group']]).\
                    get(first_name=v['research_name'].split(' ')[0],last_name=v['research_name'].split(' ')[1])
                    resperson = CollaboratorPersonInfo.objects.get(person_id=resuser,group=group_tm)
                    if v['new_email']:
                        current_email = nonetolist(resperson.email)
                        current_email.insert(0,v['new_email'])
                        resperson.email = removenone(current_email)
                    if v['new_phone']:
                        current_phone = nonetolist(resperson.phone)
                        current_phone.insert(0,v['new_phone'])
                        resperson.phone = removenone(current_phone)
                    resperson.save()

                if v['newfisinfoflag']==1:
                    fisuser = User.objects.filter(groups__name__in=[v['group']]).\
                    get(first_name=v['fiscal_name'].split(' ')[0],last_name=v['fiscal_name'].split(' ')[1])
                    fisperson = CollaboratorPersonInfo.objects.get(person_id=fisuser,group=group_tm
                        )

                    if v['fisnew_email']:
                        current_email = nonetolist(fisperson.email)
                        current_email.insert(0,v['fisnew_email'])
                        fisperson.email = removenone(current_email)
                    if v['fisnew_index']:
                        current_index = nonetolist(fisperson.index)
                        current_index.insert(0,v['fisnew_index'])
                        fisperson.index = removenone(current_index)
                    fisperson.save()
 
                tosave_item = SampleInfo(
                    sample_index=v['sample_index'],
                    group=group_tm,
                    research_name=v['research_name'],
                    research_email=v['research_email'],
                    research_phone=v['research_phone'],
                    fiscal_name=v['fiscal_name'],
                    fiscal_email=v['fiscal_email'],
                    fiscal_index=v['fiscal_index'],
                    sample_id=k,
                    species=v['species'],
                    sample_type=v['sample_type'],
                    preparation=v['preparation'],
                    description=v['description'],
                    unit=v['unit'],
                    sample_amount=v['sample_amount'],
                    fixation=v['fixation'],
                    notes=v['notes'],
                    internal_notes=v['internal_notes'],
                    team_member=User.objects.get(username=v['team_member']),
                    date=v['date'],
                    date_received=v['date_received'],
                    storage=v['storage'],
                    service_requested=v['service_requested'],
                    seq_depth_to_target=v['seq_depth_to_target'],
                    seq_length_requested=v['seq_length_requested'],
                    seq_type_requested=v['seq_type_requested'],
                )
                tosave_list.append(tosave_item)                
            SampleInfo.objects.bulk_create(tosave_list)
            return redirect('masterseq_app:index')
        if 'Preview' in request.POST:
            displayorder = ['sample_index','group','research_name','research_email',\
            'research_phone','fiscal_name', 'fiscal_email','fiscal_index','description', \
             'date','species', 'sample_type',
                            'preparation', 'fixation','sample_amount','unit',
                             'notes','service_requested','seq_depth_to_target',
                            'seq_length_requested','seq_type_requested','date_received','team_member','storage','internal_notes']
            displayorder2 = ['user_username','user_first_name','user_last_name',\
            'user_email','user_phone','user_index']
            displayorder3 = ['fisuser_username','fisuser_first_name','fisuser_last_name',\
            'fisuser_email','fisuser_phone','fisuser_index']
            displayorder4 = ['group','user_first_name','user_last_name','new_email','new_phone','new_index']
            displayorder5 = ['group','fisuser_first_name','fisuser_last_name','fisnew_email','fisnew_phone','fisnew_index']

            context = {
                'newuserrequired': newuserrequired,
                'newinforequired':newinforequired,
                'sample_form': sample_form,
                'modalshowplus': 1,
                'displayorder': displayorder,
                'displayorder2': displayorder2,
                'displayorder3': displayorder3,
                'displayorder4': displayorder4,
                'displayorder5': displayorder5,
                'data': data,
            }

            return render(request, 'masterseq_app/samplesadd.html', context)
    context = {
        'sample_form': sample_form,
    }

    return render(request, 'masterseq_app/samplesadd.html', context)



@transaction.atomic
def LibrariesCreateView(request):
    if request.user.groups.filter(name='bioinformatics').exists():
        library_form = LibsCreationForm(request.POST or None)
    else:
        library_form = LibsCreationForm_wetlab(request.POST or None)
    tosave_list = []
    data = {}
    pseudorequired = 0
    if library_form.is_valid():
        libsinfo = library_form.cleaned_data['libsinfo']
        # print(sequencinginfo)
        sampid = {}
        samp_indexes = list(SampleInfo.objects.values_list(
            'sample_index', flat=True))
        existingmaxindex = max([int(x.split('-')[1])
                                for x in samp_indexes if x.startswith('SAMPNA')])

        exp_indexes = list(LibraryInfo.objects.values_list(
            'experiment_index', flat=True))
        existingexpmaxindex = max([int(x.split('-')[1])
                                for x in exp_indexes if x.startswith('EXP-')])

        for lineitem in libsinfo.strip().split('\n'):
            lineitem = lineitem+'\t'*10
            fields = lineitem.strip('\n').split('\t')
            libid = fields[8].strip()
            sampid = fields[0].strip()
            if not SampleInfo.objects.filter(sample_id=sampid).exists():
                pseudorequired = 1
                pseudoflag = 1
                sampindex = 'SAMPNA-'+str(existingmaxindex+1)
                existingmaxindex += 1
                if sampid.strip().lower() in ['', 'na', 'other', 'n/a']:
                    sampid = sampindex

            else:
                pseudoflag = 0
                samtm = SampleInfo.objects.get(sample_id=sampid)
                sampindex = samtm.sample_index
                #saminfo = SampleInfo.objects.get(sample_index=fields[0].strip())
            expindex = 'EXP-'+str(existingexpmaxindex+1)
            existingexpmaxindex = existingexpmaxindex+1
            data[libid] = {}
            datestart = datetransform(fields[3].strip())
            dateend = datetransform(fields[4].strip())
            libexp = fields[5].strip()
            # libprotocal = ProtocalInfo.objects.get(
            # experiment_type=libexp, protocal_name='other (please explain in notes)')
            refnotebook = fields[7].strip()
            #libnote = ';'.join([fields[9].strip(), 'Protocol used(recorded in Tracking Sheet 2):', fields[6].strip()]).strip(';')
            libnote = fields[9].strip()
            #memebername = User.objects.get(username=fields[2].strip())
            data[libid] = {
                'pseudoflag': pseudoflag,
                'sampleinfo': sampid,
                'sample_index': sampindex,
                'sample_id': sampid,
                'lib_description': fields[1].strip(),
                'team_member_initails': fields[2].strip(),
                'experiment_index': expindex,
                'date_started': datestart,
                'date_completed': dateend,
                'experiment_type': libexp,
                'protocal_name': fields[6].strip(),
                'reference_to_notebook_and_page_number': fields[7].strip(),
                'notes': libnote
            }

        if 'Save' in request.POST:
            for k, v in data.items():
                if v['pseudoflag'] == 1:
                    SampleInfo.objects.create(
                        sample_id=v['sample_id'],
                        sample_index=v['sample_index'],
                        team_member=User.objects.get(
                            username=v['team_member_initails']),
                    )
                tosave_item = LibraryInfo(
                    library_id=k,
                    library_description=v['lib_description'],
                    sampleinfo=SampleInfo.objects.get(
                        sample_id=v['sampleinfo']),
                    experiment_index=v['experiment_index'],
                    experiment_type=v['experiment_type'],
                    protocal_used=v['protocal_name'],
                    reference_to_notebook_and_page_number=v['reference_to_notebook_and_page_number'],
                    date_started=v['date_started'],
                    date_completed=v['date_completed'],
                    team_member_initails=User.objects.get(
                        username=v['team_member_initails']),
                    notes=v['notes']
                )
                tosave_list.append(tosave_item)
            LibraryInfo.objects.bulk_create(tosave_list)
            return redirect('masterseq_app:index')
        if 'Preview' in request.POST:
            displayorder = ['sampleinfo','lib_description','team_member_initails', 'experiment_index', 'date_started',
                            'date_completed', 'experiment_type', 'protocal_name', 'reference_to_notebook_and_page_number',
                            'notes']
            if pseudorequired == 1:
                displayorder2 = ['sample_index',
                                 'sample_id', 'team_member_initails']
                context = {
                    'library_form': library_form,
                    'modalshowplus': 1,
                    'displayorder': displayorder,
                    'displayorder2': displayorder2,
                    'data': data,
                }

                return render(request, 'masterseq_app/libsadd.html', context)

            else:
                context = {
                    'library_form': library_form,
                    'modalshow': 1,
                    'displayorder': displayorder,
                    'data': data,
                }

                return render(request, 'masterseq_app/libsadd.html', context)

        if 'PreviewfromWarning' in request.POST:
            displayorder = ['sampleinfo','lib_description','team_member_initails', 'experiment_index', 'date_started',
                            'date_completed', 'experiment_type', 'protocal_name', 'reference_to_notebook_and_page_number',
                            'notes']
            displayorder2 = ['sample_index',
                             'sample_id', 'team_member_initails']
            context = {
                'library_form': library_form,
                'modalshowplusfromwarning': 1,
                'displayorder': displayorder,
                'displayorder2': displayorder2,
                'data': data,
            }

            return render(request, 'masterseq_app/libsadd.html', context)



        if 'Warning' in request.POST:
            displayorder3 = ['sample_id']
            context = {
                'library_form': library_form,
                'warningmodalshow': 1,
                'displayorder3': displayorder3,
                'data': data,
            }

            return render(request, 'masterseq_app/libsadd.html', context)

    context = {
        'library_form': library_form,
    }

    return render(request, 'masterseq_app/libsadd.html', context)


@transaction.atomic
def SeqsCreateView(request):
    if request.user.groups.filter(name='bioinformatics').exists():
        seqs_form = SeqsCreationForm(request.POST or None)
    else:
        seqs_form = SeqsCreationForm_wetlab(request.POST or None)
    tosave_list = []
    data = {}
    updatesamprequired = 0
    pseudosamprequired = 0
    pseudolibrequired = 0
    if seqs_form.is_valid():
        seqsinfo = seqs_form.cleaned_data['seqsinfo']
        samp_indexes = list(SampleInfo.objects.values_list(
            'sample_index', flat=True))
        existingmaxsampindex = max([int(x.split('-')[1])
                                    for x in samp_indexes if x.startswith('SAMPNA')])
        lib_indexes = list(LibraryInfo.objects.values_list(
            'experiment_index', flat=True))
        existingmaxlibindex = max([int(x.split('-')[1])
                                   for x in lib_indexes if x.startswith('EXPNA')])

        for lineitem in seqsinfo.strip().split('\n'):
            lineitem = lineitem+'\t'*20
            fields = lineitem.split('\t')
            updatesampflag = 0
            pseudolibflag = 0
            pseudosamflag = 0
            #samindex = fields[0].strip()
            sampid = fields[0].strip()
            sampspecies = fields[2].strip().lower()
            seqid = fields[6].strip()
            #expindex = fields[4].strip()
            libraryid = fields[5].strip()
            exptype = fields[7].strip()
            data[seqid] = {}
            if not LibraryInfo.objects.filter(library_id=libraryid).exists():
                pseudolibrequired = 1
                pseudolibflag = 1
                expindex = 'EXPNA-'+str(existingmaxlibindex+1)
                existingmaxlibindex += 1
                if not SampleInfo.objects.filter(sample_id=sampid).exists():
                    pseudosamprequired = 1
                    pseudosamflag = 1
                    sampindex = 'SAMPNA-'+str(existingmaxsampindex+1)
                    existingmaxsampindex += 1
                    if sampid.strip().lower() in ['', 'na', 'other', 'n/a']:
                        sampid = sampindex
                else:
                    sampinfo = SampleInfo.objects.get(sample_id=sampid)
                    sampindex = sampinfo.sample_index
                    if not sampinfo.species and sampspecies:
                        updatesampflag = 1
                        updatesamprequired = 1
            else:
                libinfo = LibraryInfo.objects.select_related(
                    'sampleinfo').get(library_id=libraryid)
                sampinfo = libinfo.sampleinfo
                sampindex = sampinfo.sample_index
                sampid = sampinfo.sample_id
                expindex = libinfo.experiment_index

                if not sampinfo.species and sampspecies:
                    updatesampflag = 1
                    updatesamprequired = 1

            if '-' in fields[4].strip():
                datesub = fields[4].strip()
            else:
                datesub = datetransform(fields[4].strip())
            memebername = User.objects.get(username=fields[3].strip())
            indexname = fields[13].strip()
            if indexname and indexname not in ['NA', 'Other (please explain in notes)', 'N/A']:
                i7index = Barcode.objects.get(indexid=indexname)
            else:
                i7index = None
            indexname2 = fields[14].strip()
            if indexname2 and indexname2 not in ['NA', 'Other (please explain in notes)', 'N/A']:
                i5index = Barcode.objects.get(indexid=indexname2)
            else:
                i5index = None
            polane = fields[12].strip()
            if polane and polane not in ['NA', 'Other (please explain in notes)', 'N/A']:
                polane = float(polane)
            else:
                polane = None
            seqid = fields[6].strip()
            seqcore = fields[8].split('(')[0].strip()
            seqmachine = fields[9].split('(')[0].strip()
            machineused = SeqMachineInfo.objects.get(
                sequencing_core=seqcore, machine_name=seqmachine)
            data[seqid] = {
                'updatesampflag': updatesampflag,
                'pseudolibflag': pseudolibflag,
                'pseudosamflag': pseudosamflag,
                'sample_index': sampindex,
                'sampleinfo': sampid,
                'sample_id': sampid,
                'species': sampspecies,
                'experiment_index': expindex,
                'experiment_type': exptype,
                'libraryinfo': fields[5].strip(),
                'library_id': libraryid,
                'default_label': fields[1].strip(),
                'team_member_initails': fields[3].strip(),
                'read_length': fields[10].strip(),
                'read_type': fields[11].strip(),
                'portion_of_lane': polane,
                'seqcore': fields[8].split('(')[0].strip(),
                'machine': seqmachine,
                'i7index': indexname,
                'i5index': indexname2,
                'indexname': indexname,
                'indexname2': indexname2,
                'date_submitted': datesub,
                'notes': fields[15].strip(),
            }
        if 'Save' in request.POST:

            for k, v in data.items():
                if v['pseudolibflag'] == 1:
                    if v['pseudosamflag'] == 1:
                        SampleInfo.objects.create(
                            sample_id=v['sample_id'],
                            sample_index=v['sample_index'],
                            species=v['species'],
                            team_member=User.objects.get(
                                username=v['team_member_initails']),
                        )

                    LibraryInfo.objects.create(
                        library_id=v['library_id'],
                        experiment_index=v['experiment_index'],
                        experiment_type=v['experiment_type'],
                        sampleinfo=SampleInfo.objects.get(
                            sample_index=v['sample_index']),
                        team_member_initails=User.objects.get(
                            username=v['team_member_initails']),
                    )
                if v['updatesampflag'] == 1:
                    sampleinfo = SampleInfo.objects.get(
                        sample_index=v['sample_index'])
                    sampleinfo.species = v['species']
                    sampleinfo.save()
                if v['indexname'] and v['indexname'] not in ['NA', 'Other (please explain in notes)', 'N/A']:
                    i7index = Barcode.objects.get(indexid=v['indexname'])
                else:
                    i7index = None
                if v['indexname2'] and v['indexname2'] not in ['NA', 'Other (please explain in notes)', 'N/A']:
                    i5index = Barcode.objects.get(indexid=v['indexname2'])
                else:
                    i5index = None
                tosave_item = SeqInfo(
                    seq_id=k,
                    libraryinfo=LibraryInfo.objects.get(
                        library_id=v['library_id']),
                    team_member_initails=User.objects.get(
                        username=v['team_member_initails']),
                    read_length=v['read_length'],
                    read_type=v['read_type'],
                    portion_of_lane=v['portion_of_lane'],
                    notes=v['notes'],
                    machine=SeqMachineInfo.objects.get(
                        sequencing_core=v['seqcore'], machine_name=v['machine']),
                    i7index=i7index,
                    i5index=i5index,
                    default_label=v['default_label'],
                    date_submitted_for_sequencing=v['date_submitted'],
                )
                tosave_list.append(tosave_item)
            SeqInfo.objects.bulk_create(tosave_list)
            return redirect('masterseq_app:index')
        if 'Preview' in request.POST:
            displayorder = ['libraryinfo', 'default_label', 'date_submitted', 'team_member_initails', 'read_length',
                            'read_type', 'portion_of_lane', 'seqcore', 'machine', 'i7index', 'i5index', 'notes']
            displayorder2 = ['sample_index', 'sample_id',
                             'species', 'team_member_initails']
            displayorder3 = ['library_id', 'sampleinfo',
                             'experiment_index', 'experiment_type', 'team_member_initails']
            context = {
                'updatesamprequired': updatesamprequired,
                'pseudosamprequired': pseudosamprequired,
                'pseudolibrequired': pseudolibrequired,
                'seqs_form': seqs_form,
                'modalshowplus': 1,
                'displayorder': displayorder,
                'displayorder2': displayorder2,
                'displayorder3': displayorder3,
                'data': data,
            }

            return render(request, 'masterseq_app/seqsadd.html', context)
        if 'PreviewfromWarning' in request.POST:
            displayorder = ['libraryinfo', 'default_label', 'date_submitted', 'team_member_initails', 'read_length',
                            'read_type', 'portion_of_lane', 'seqcore', 'machine', 'i7index', 'i5index', 'notes']
            displayorder2 = ['sample_index', 'sample_id',
                             'species', 'team_member_initails']
            displayorder3 = ['library_id', 'sampleinfo',
                             'experiment_index', 'experiment_type', 'team_member_initails']
            context = {
                'updatesamprequired': updatesamprequired,
                'pseudosamprequired': pseudosamprequired,
                'pseudolibrequired': pseudolibrequired,
                'seqs_form': seqs_form,
                'modalshowplusfromwarning': 1,
                'displayorder': displayorder,
                'displayorder2': displayorder2,
                'displayorder3': displayorder3,
                'data': data,
            }

            return render(request, 'masterseq_app/seqsadd.html', context)

        if 'Warning' in request.POST:
            displayorder4 = ['library_id']
            displayorder5 = ['sample_id']
            context = {
                'pseudosamprequired': pseudosamprequired,
                'seqs_form': seqs_form,
                'warningmodalshow': 1,
                'displayorder4': displayorder4,
                'displayorder5': displayorder5,
                'data': data,
            }

            return render(request, 'masterseq_app/seqsadd.html', context)



    context = {
        'seqs_form': seqs_form,
    }

    return render(request, 'masterseq_app/seqsadd.html', context)

# @transaction.atomic
# def SeqsCreateConfirmView(request,seqsdata):
#     data = {}
#     for lineitem in seqsdata.strip().split('\n'):
#         lineitem = lineitem+'\t\t\t\t\t\t'
#         fields = lineitem.split('\t')
#         seqid = fields[8].strip()
#         data[seqid] = {}
#         libinfo = LibraryInfo.objects.get(library_id = fields[7].strip())
#         if '-' in fields[6].strip():
#             datesub = fields[6].strip()
#         else:
#             datesub = datetransform(fields[6].strip())
#         memebername = User.objects.get(username=fields[5].strip())
#         indexname = fields[15].strip()
#         if indexname and indexname not in ['NA','Other (please explain in notes)','N/A']:
#             i7index = Barcode.objects.get(indexid=indexname)
#         else:
#             i7index = None
#         indexname2 = fields[16].strip()
#         if indexname2 and indexname2 not in ['NA','Other (please explain in notes)','N/A']:
#             i5index = Barcode.objects.get(indexid=indexname2)
#         else:
#             i5index = None
#         polane = fields[14].strip()
#         if polane and polane not in ['NA','Other (please explain in notes)','N/A']:
#             polane = float(polane)
#         else:
#             polane = None

#         seqcore = fields[10].split('(')[0].strip()
#         seqmachine = fields[11].split('(')[0].strip()
#         machineused = SeqMachineInfo.objects.get(sequencing_core = seqcore,machine_name = seqmachine)
#         data[seqid] = {
#             'libraryinfo':fields[7].strip(),
#             'default_label':fields[2].strip(),
#             'team_member_initails':fields[5].strip(),
#             'read_length':fields[12].strip(),
#             'read_type':fields[13].strip(),
#             'portion_of_lane':fields[14].strip(),
#             'seqcore':fields[10].split('(')[0].strip(),
#             'machine':seqmachine,
#             'i7index':indexname,
#             'i5index':indexname2,
#             'date':datesub,
#             'notes':fields[17].strip(),
#         }
#         tosave_item = SeqInfo(
#             seq_id = seqid,
#             libraryinfo = libinfo,
#             team_member_initails = memebername,
#             read_length = fields[12].strip(),
#             read_type = fields[13].strip(),
#             portion_of_lane = polane,
#             notes = fields[17].strip(),
#             machine = machineused,
#             i7index = i7index,
#             i5index = i5index,
#             default_label = fields[2].strip(),
#             date_submitted_for_sequencing = datesub,
#             )
#         tosave_list.append(tosave_item)
#     if request.method == "POST":
#         SeqInfo.objects.bulk_create(tosave_list)
#         return redirect('masterseq_app:index')
#     else:
#         displayorder = ['libraryinfo','default_label','team_member_initails','read_length',\
#         'read_type','portion_of_lane','seqcore','machine','i7index','i5index','date','notes']
#         context = {
#             'displayorder': displayorder,
#             'data':data
#         }

#         return render(request, 'masterseq_app/seqsaddconfirm.html', context)


def SampleDataView(request):
    Samples_list = SampleInfo.objects.all().select_related('group').values(
        'pk', 'sample_id', 'description', 'date', 'sample_type', 'group__name', 'status')
    for sample in Samples_list:
        try:
            sample['group__name'] = sample['group__name'].replace(
                '_group', '').replace('_', ' ')
        except:
            pass
    data = list(Samples_list)

    return JsonResponse(data, safe=False)


def LibDataView(request):
    Libs_list = LibraryInfo.objects.all().select_related('sampleinfo__group').values(
        'pk', 'library_id', 'library_description','sampleinfo__id', 'sampleinfo__sample_type', 'sampleinfo__sample_id', 'sampleinfo__description',
        'sampleinfo__species', 'sampleinfo__group__name', 'date_started', 'experiment_type')
    data = list(Libs_list)

    return JsonResponse(data, safe=False)


def SeqDataView(request):
    Seqs_list = SeqInfo.objects.all().select_related('libraryinfo__sampleinfo__group').values(
        'pk', 'seq_id', 'libraryinfo__library_description','libraryinfo__sampleinfo__id', 'libraryinfo__sampleinfo__sample_id',
        'libraryinfo__sampleinfo__description', 'libraryinfo__sampleinfo__group__name', \
        'date_submitted_for_sequencing','machine__sequencing_core',\
        'machine__machine_name','portion_of_lane','read_length', 'read_type')
    data = list(Seqs_list)

    return JsonResponse(data, safe=False)


def UserSampleDataView(request):
    Samples_list = SampleInfo.objects.filter(team_member=request.user).values(
        'pk', 'sample_id', 'description', 'date', 'sample_type', 'group__name', 'status')
    for sample in Samples_list:
        try:
            sample['group__name'] = sample['group__name'].replace(
                '_group', '').replace('_', ' ')
        except:
            pass
    data = list(Samples_list)

    return JsonResponse(data, safe=False)


def UserLibDataView(request):
    Libs_list = LibraryInfo.objects.filter(team_member_initails=request.user)\
        .select_related('sampleinfo__group').values(
            'pk', 'library_description','library_id', 'sampleinfo__id',  'sampleinfo__sample_type', 'sampleinfo__sample_id', 'sampleinfo__description',
        'sampleinfo__species', 'sampleinfo__group__name', 'date_started', 'experiment_type')
    data = list(Libs_list)

    return JsonResponse(data, safe=False)


def UserSeqDataView(request):
    Seqs_list = SeqInfo.objects.filter(team_member_initails=request.user)\
        .select_related('libraryinfo__sampleinfo__group','machine').values(
        'pk', 'seq_id','libraryinfo__library_description', 'libraryinfo__sampleinfo__id', 'libraryinfo__sampleinfo__sample_id',
        'libraryinfo__sampleinfo__description', 'libraryinfo__sampleinfo__group__name',
        'date_submitted_for_sequencing','machine__sequencing_core',\
        'machine__machine_name','portion_of_lane','read_length', 'read_type')
    data = list(Seqs_list)

    return JsonResponse(data, safe=False)


def IndexView(request):
    if not request.user.groups.filter(name='bioinformatics').exists():
        return render(request, 'masterseq_app/metadata.html')
    else:
        # sample_disp = ['sample_id','date','sample_type','service_requested','status']
        # Samples_list = SampleInfo.objects.all().values(\
        #    'pk','sample_id','date','sample_type','service_requested','status')
        # #print(Samples_list)
        # #sample_data=list(Samples_list)
        # libs_disp = ['library_id','date_started','date_completed','experiment_type']
        # Libs_list = LibraryInfo.objects.all().values(\
        #     'pk','library_id','date_started','date_completed','experiment_type')
        # #data=list(Libs_list)
        # seqs_disp = ['seq_id','date_submitted_for_sequencing','read_length','read_type']
        # Seqs_list = SeqInfo.objects.all().values(\
        #     'pk','seq_id','date_submitted_for_sequencing','read_length','read_type')
        # #data=list(Seqs_list)
        # #print(data)
        # context = {
        #     'sample_disp': sample_disp,
        #     'Samples_list': Samples_list,
        #     'libs_disp':libs_disp,
        #     'Libs_list ': Libs_list,
        #     'seqs_disp':seqs_disp,
        #     'Seqs_list': Seqs_list,
        # }
        # return render(request, 'masterseq_app/metadata_bio.html',context=context)
        return render(request, 'masterseq_app/metadata_bio.html')


def UserMetaDataView(request):
    if not request.user.groups.filter(name='bioinformatics').exists():
        return render(request, 'masterseq_app/metadata.html')
    else:
        # sample_disp = ['sample_id','date','sample_type','service_requested','status']
        # Samples_list = SampleInfo.objects.all().values(\
        #    'pk','sample_id','date','sample_type','service_requested','status')
        # #print(Samples_list)
        # #sample_data=list(Samples_list)
        # libs_disp = ['library_id','date_started','date_completed','experiment_type']
        # Libs_list = LibraryInfo.objects.all().values(\
        #     'pk','library_id','date_started','date_completed','experiment_type')
        # #data=list(Libs_list)
        # seqs_disp = ['seq_id','date_submitted_for_sequencing','read_length','read_type']
        # Seqs_list = SeqInfo.objects.all().values(\
        #     'pk','seq_id','date_submitted_for_sequencing','read_length','read_type')
        # #data=list(Seqs_list)
        # #print(data)
        # context = {
        #     'sample_disp': sample_disp,
        #     'Samples_list': Samples_list,
        #     'libs_disp':libs_disp,
        #     'Libs_list ': Libs_list,
        #     'seqs_disp':seqs_disp,
        #     'Seqs_list': Seqs_list,
        # }
        # return render(request, 'masterseq_app/metadata_bio.html',context=context)
        return render(request, 'masterseq_app/metadata_bio.html')


def SampleDeleteView(request, pk):
    sampleinfo = get_object_or_404(SampleInfo, pk=pk)
    if sampleinfo.team_member != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    sampleinfo.delete()
    return redirect('masterseq_app:user_metadata')


def LibDeleteView(request, pk):
    libinfo = get_object_or_404(LibraryInfo, pk=pk)
    if libinfo.team_member_initails != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    libinfo.delete()
    return redirect('masterseq_app:user_metadata')


def SeqDeleteView(request, pk):
    seqinfo = get_object_or_404(SeqInfo, pk=pk)
    if seqinfo.team_member_initails != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    seqinfo.delete()
    return redirect('masterseq_app:user_metadata')


@transaction.atomic
def SampleUpdateView(request, pk):
    sampleinfo = get_object_or_404(SampleInfo, pk=pk)
    orig_team_member = sampleinfo.team_member
    if sampleinfo.team_member != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    sample_form = SampleCreationForm(request.POST or None, instance=sampleinfo)
    if sample_form.is_valid():
        sampleinfo = sample_form.save(commit=False)
        sampleinfo.team_member = orig_team_member
        sampleinfo.save()
        return redirect('masterseq_app:user_metadata')
    context = {
        'sample_form': sample_form,
        'sampleinfo': sampleinfo,
    }

    return render(request, 'masterseq_app/sampleupdate.html', context)


@transaction.atomic
def LibUpdateView(request, pk):
    libinfo = get_object_or_404(LibraryInfo, pk=pk)
    if libinfo.team_member_initails != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied

    if request.method == 'POST':
        post = request.POST.copy()
        obj = get_object_or_404(
            SampleInfo, sample_index=post['sampleinfo'].split(':')[0])
        post['sampleinfo'] = obj.id
        library_form = LibraryCreationForm(post, instance=libinfo)
        if library_form.is_valid():
            libinfo = library_form.save(commit=False)
            libinfo.team_member_initails = request.user
            libinfo.save()
            return redirect('masterseq_app:user_metadata')
    else:
        library_form = LibraryCreationForm(instance=libinfo)

    context = {
        'library_form': library_form,
        'libinfo': libinfo,
    }

    return render(request, 'masterseq_app/libraryupdate.html', context)


@transaction.atomic
def SeqUpdateView(request, pk):
    seqinfo = get_object_or_404(SeqInfo, pk=pk)
    if seqinfo.team_member_initails != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied

    if request.method == 'POST':
        post = request.POST.copy()
        obj = get_object_or_404(LibraryInfo, library_id=post['libraryinfo'])
        post['libraryinfo'] = obj.id
        seq_form = SeqCreationForm(post, instance=seqinfo)
        if seq_form.is_valid():
            seqinfo = seq_form.save(commit=False)
            seqinfo.team_member_initails = request.user
            seqinfo.save()
            return redirect('masterseq_app:user_metadata')
    else:
        seq_form = SeqCreationForm(instance=seqinfo)

    context = {
        'seq_form': seq_form,
        'seqinfo': seqinfo,
    }

    return render(request, 'masterseq_app/sequpdate.html', context)


def SampleDetailView(request, pk):
    sampleinfo = get_object_or_404(SampleInfo.objects.select_related(
        'team_member', 'research_person__person_id', 'fiscal_person__person_id'), pk=pk)
    summaryfield = ['status', 'sample_index', 'sample_id', 'description', 'date', 'species',
                    'sample_type', 'preparation', 'fixation', 'sample_amount', 'unit', 'notes','date_received','team_member','storage', 'internal_notes']
    requestedfield = ['date', 'service_requested', 'seq_depth_to_target',
                      'seq_length_requested', 'seq_type_requested']
    libfield = ['library_id', 'experiment_type',
                'protocalinfo', 'reference_to_notebook_and_page_number']
    seqfield = ['seq_id', 'default_label', 'machine',
                'read_length', 'read_type', 'total_reads']
    libinfo = sampleinfo.libraryinfo_set.all().select_related('protocalinfo')
    seqs = SeqInfo.objects.none()
    try:
        researchperson=CollaboratorPersonInfo.objects.get(email__contains=[sampleinfo.research_email])
        researchperson_name=researchperson.person_id.first_name+' '+researchperson.person_id.last_name
    except:
        researchperson_name=''
    try:
        fiscalperson=CollaboratorPersonInfo.objects.get(email__contains=[sampleinfo.fiscal_email])
        fiscalperson_name=fiscalperson.person_id.first_name+' '+fiscalperson.person_id.last_name
    except:
        fiscalperson_name=''
    for lib in libinfo:
        seqinfo = lib.seqinfo_set.all().select_related('machine')
        seqs = seqs | seqinfo
    groupinfo = sampleinfo.group
    piname = []
 
    if groupinfo:
        for user in groupinfo.user_set.all():
            for person in user.collaboratorpersoninfo_set.all():
                if 'PI' in person.role:
                    piname.append(user.first_name + ' ' + user.last_name)

    context = {
        'groupinfo': groupinfo,
        'piname': ';'.join(piname),
        'researchperson_name': researchperson_name,
        'fiscalperson_name': fiscalperson_name,
        'summaryfield': summaryfield,
        'requestedfield': requestedfield,
        'sampleinfo': sampleinfo,
        'libfield': libfield,
        'seqfield': seqfield,
        'libinfo': libinfo.order_by('library_id'),
        'seqs': seqs.order_by('seq_id')
    }
    return render(request, 'masterseq_app/sampledetail.html', context=context)


def LibDetailView(request, pk):
    libinfo = get_object_or_404(LibraryInfo.objects.select_related('sampleinfo',
                                                                   'protocalinfo', 'team_member_initails'), pk=pk)
    sampleinfo = libinfo.sampleinfo
    summaryfield = ['library_id','library_description','sampleinfo', 'date_started', 'date_completed',
                    'team_member_initails', 'experiment_type', 'protocal_used',
                    'reference_to_notebook_and_page_number', 'notes']
    seqfield = ['seq_id', 'default_label', 'machine',
                'read_length', 'read_type', 'total_reads']
    relateseq = libinfo.seqinfo_set.all().only(
        'seq_id', 'machine', 'read_length', 'read_type', 'total_reads')
    context = {
        'libinfo': libinfo,
        'sampleinfo': sampleinfo,
        'summaryfield': summaryfield,
        'relateseq': relateseq.order_by('seq_id'),
        'seqfield': seqfield
    }
    return render(request, 'masterseq_app/libdetail.html', context=context)


def SeqDetailView(request, pk):
    seqinfo = get_object_or_404(SeqInfo.objects.select_related('libraryinfo',
                                                               'machine', 'i7index', 'i5index', 'team_member_initails'), pk=pk)
    libinfo = seqinfo.libraryinfo
    saminfo = libinfo.sampleinfo
    summaryfield = ['seq_id', 'sampleinfo', 'libraryinfo', 'default_label', 'team_member_initails',
                    'date_submitted_for_sequencing', 'machine', 'read_length', 'read_type', 'portion_of_lane',
                    'i7index', 'i5index', 'total_reads', 'notes']
    bioinfofield = ['genome', 'pipeline_version', 'final_reads', 'final_yield', 'mito_frac',
                    'tss_enrichment', 'frop']
    seqbioinfos = seqinfo.seqbioinfo_set.all().select_related('genome')
    context = {
        'libinfo': libinfo,
        'saminfo': saminfo,
        'seqinfo': seqinfo,
        'summaryfield': summaryfield,
        'seqbioinfos': seqbioinfos,
        'bioinfofield': bioinfofield

    }
    return render(request, 'masterseq_app/seqdetail.html', context=context)


def SeqDetail2View(request, seqid):
    seqinfo = get_object_or_404(SeqInfo.objects.select_related('libraryinfo',
                                                               'machine', 'i7index', 'i5index', 'team_member_initails'), seq_id=seqid)
    libinfo = seqinfo.libraryinfo
    saminfo = libinfo.sampleinfo
    summaryfield = ['seq_id', 'sampleinfo', 'libraryinfo', 'default_label', 'team_member_initails',
                    'date_submitted_for_sequencing', 'machine', 'read_length', 'read_type', 'portion_of_lane',
                    'i7index', 'i5index', 'total_reads', 'notes']
    bioinfofield = ['genome', 'pipeline_version', 'final_reads', 'final_yield', 'mito_frac',
                    'tss_enrichment', 'frop']
    seqbioinfos = seqinfo.seqbioinfo_set.all().select_related('genome')
    context = {
        'libinfo': libinfo,
        'saminfo': saminfo,
        'seqinfo': seqinfo,
        'summaryfield': summaryfield,
        'seqbioinfos': seqbioinfos,
        'bioinfofield': bioinfofield

    }
    return render(request, 'masterseq_app/seqdetail.html', context=context)


def load_samples(request):
    q = request.GET.get('term', '')
    samples = SampleInfo.objects.filter(Q(sample_id__icontains=q) | Q(
        sample_index__icontains=q)).values('sample_index', 'sample_id')[:20]
    results = []
    for sample in samples:
        samplesearch = {}
        samplesearch['id'] = sample['sample_index']+':'+sample['sample_id']
        samplesearch['label'] = sample['sample_index']+':'+sample['sample_id']
        samplesearch['value'] = sample['sample_index']+':'+sample['sample_id']
        results.append(samplesearch)
    return JsonResponse(results, safe=False)


def load_libs(request):
    q = request.GET.get('term', '')
    libs = LibraryInfo.objects.filter(
        library_id__icontains=q).values('library_id')[:20]
    results = []
    for lib in libs:
        libsearch = {}
        libsearch['id'] = lib['library_id']
        libsearch['label'] = lib['library_id']
        libsearch['value'] = lib['library_id']
        results.append(libsearch)
    return JsonResponse(results, safe=False)

def SaveMyMetaDataExcel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="MyMetaData.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Samples')
    row_num = 0 
    style = xlwt.XFStyle()
    style.font.bold = True
    style.alignment.wrap = 1
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN    
    pattern.pattern_fore_colour = xlwt.Style.colour_map['turquoise']
    style.pattern = pattern
    borders = xlwt.Borders()
    borders.left = 1
    borders.right = 1
    borders.top = 1
    borders.bottom = 1
    style.borders = borders

    row_num = 0 
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 256*1
    ws.write_merge(0, 0, 0, 20, 'From sample submission form', style)
    style = xlwt.XFStyle()
    style.font.bold = True
    style.alignment.wrap = 1
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN    
    pattern.pattern_fore_colour = xlwt.Style.colour_map['light_green']
    style.pattern = pattern
    borders = xlwt.Borders()
    borders.left = 1
    borders.right = 1
    borders.top = 1
    borders.bottom = 1
    style.borders = borders

    row_num = 0 
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 256*1
    ws.write_merge(0, 0, 21, 24, 'To be entered upon reciept', style)
    row_num = 1
    columns_width = [15,15,15,21,15,15,21,15,25,30,12,15,15,11,12,12,12,12,12,12,30,15,15,15,25]
    columns = ['Date','PI','Research contact name','Research contact e-mail',\
    'Research contact phone','Fiscal contact name','Fiscal conact e-mail','Index for payment',\
    'Sample ID','Sample description','Species','Sample type','Preperation',\
    'Fixation?','Sample amount','Units','Service requested','Sequencing depth to target',\
    'Sequencing length requested','Sequencing type requested', 'Notes',\
    'Date sample received','team member','Storage location','Internal_Notes'] 

    for col_num in range(len(columns)):
        ws.col(col_num).width = 256*columns_width[col_num]
        if col_num == 8:
            style = xlwt.XFStyle()
            style.alignment.wrap = 1
            style.font.bold = True
            #first_col = ws.col(0)
            #first_col.width = 256 * 6
            ws.row(row_num).height_mismatch = True
            ws.row(row_num).height = 256*3
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN    
            pattern.pattern_fore_colour = 5
            style.pattern = pattern
            borders = xlwt.Borders()
            borders.left = 1
            borders.right = 1
            borders.top = 1
            borders.bottom = 1
            style.borders = borders
            ws.write(row_num, col_num, columns[col_num], style)

        else:
            style = xlwt.XFStyle()
            style.alignment.wrap = 1
            style.font.bold = True
            #first_col = ws.col(0)
            #first_col.width = 256 * 6
            ws.row(row_num).height_mismatch = True
            ws.row(row_num).height = 256*3
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN    
            pattern.pattern_fore_colour = 22
            style.pattern = pattern
            borders = xlwt.Borders()
            borders.left = 1
            borders.right = 1
            borders.top = 1
            borders.bottom = 1
            style.borders = borders
            ws.write(row_num, col_num, columns[col_num], style)
    Samples_list = SampleInfo.objects.filter(team_member=request.user).order_by('pk').select_related('group',\
        'team_member').values_list('date','group__name',\
        'research_name','research_email','research_phone','fiscal_name','fiscal_email','fiscal_index',\
        'sample_id','description','species','sample_type',\
        'preparation','fixation','sample_amount','unit','service_requested','seq_depth_to_target',\
        'seq_length_requested','seq_type_requested','notes','date_received',\
        'team_member__username','storage','internal_notes'
        )
    #print(list(Samples_list))
    #print(len(Samples_list))
    rows = Samples_list
    font_style = xlwt.XFStyle()
    #rows = User.objects.all().values_list('username', 'first_name', 'last_name', 'email')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str((row[col_num] or '')), font_style)
    wl = wb.add_sheet('Libraries')
    row_num = 0

    columns_width = [30,25,12,15,15,15,20,20,15,30]
    columns = ['Sample ID (Must Match Column I in Sample Sheet)','Library description','Team member intials','Date experiment started','Date experiment completed',\
    'Experiment type','Protocol used','Reference to notebook and page number','library_id',
    'notes'] 

    for col_num in range(len(columns)):
        wl.col(col_num).width = 256*columns_width[col_num]
        if col_num == 0:
            style = xlwt.XFStyle()
            style.alignment.wrap = 1
            style.font.bold = True
            #first_col = ws.col(0)
            #first_col.width = 256 * 6
            wl.row(row_num).height_mismatch = True
            wl.row(row_num).height = 256*3
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN    
            pattern.pattern_fore_colour = 5
            style.pattern = pattern
            borders = xlwt.Borders()
            borders.left = 1
            borders.right = 1
            borders.top = 1
            borders.bottom = 1
            style.borders = borders

        else:
            style = xlwt.XFStyle()
            style.alignment.wrap = 1
            style.font.bold = True
            #first_col = ws.col(0)
            #first_col.width = 256 * 6
            wl.row(row_num).height_mismatch = True
            wl.row(row_num).height = 256*3
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN    
            pattern.pattern_fore_colour = 22
            style.pattern = pattern
            borders = xlwt.Borders()
            borders.left = 1
            borders.right = 1
            borders.top = 1
            borders.bottom = 1
            style.borders = borders
        wl.write(row_num, col_num, columns[col_num], style)
    Libraries_list = LibraryInfo.objects.filter(team_member_initails=request.user).order_by('pk').select_related(\
        'team_member_initails','sampleinfo').values_list('sampleinfo__sample_id','library_description','team_member_initails__username','date_started',\
        'date_completed','experiment_type','protocal_used',\
        'reference_to_notebook_and_page_number','library_id','notes')

    rows = Libraries_list
    font_style = xlwt.XFStyle()
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            wl.write(row_num, col_num, str((row[col_num] or '')), font_style)

    we = wb.add_sheet('Sequencings')
    row_num = 0

    columns_width = [30,25,12,12,20,15,15,15,15,15,15,12,10,12,12,30,15,15,15,15,15,15,15,15]
    columns = ['Sample ID (Must Match Column I in Sample Sheet)','Label (for QC report)','Species',\
    'Team member intials','Date submitted for sequencing','Library ID','Sequencing ID','Experiment type',\
    'Sequening core','Machine','Sequening length','Read type','Portion of lane',\
    'i7 index (if applicable)','i5 Index (or single index','Notes','pipeline_version','Genome','total_reads',\
    'final_reads','final_yield','mito_frac','tss_enrichment','frop'] 
    for col_num in range(len(columns)):
        we.col(col_num).width = 256*columns_width[col_num]
        if col_num == 0:
            style = xlwt.XFStyle()
            style.alignment.wrap = 1
            style.font.bold = True
            #first_col = ws.col(0)
            #first_col.width = 256 * 6
            we.row(row_num).height_mismatch = True
            we.row(row_num).height = 256*3
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN    
            pattern.pattern_fore_colour = 5
            style.pattern = pattern
            borders = xlwt.Borders()
            borders.left = 1
            borders.right = 1
            borders.top = 1
            borders.bottom = 1
            style.borders = borders

        else:
            style = xlwt.XFStyle()
            style.alignment.wrap = 1
            style.font.bold = True
            #first_col = ws.col(0)
            #first_col.width = 256 * 6
            we.row(row_num).height_mismatch = True
            we.row(row_num).height = 256*3
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN    
            pattern.pattern_fore_colour = 22
            style.pattern = pattern
            borders = xlwt.Borders()
            borders.left = 1
            borders.right = 1
            borders.top = 1
            borders.bottom = 1
            style.borders = borders
        we.write(row_num, col_num, columns[col_num], style)
    Seqs_list = SeqInfo.objects.filter(team_member_initails=request.user).order_by('pk').select_related('libraryinfo',\
        'libraryinfo__sampleinfo','team_member_initails','machine','i7index','i5index').\
    prefetch_related(Prefetch('seqbioinfo_set__genome')).values_list(\
        'libraryinfo__sampleinfo__sample_id',\
        'default_label','libraryinfo__sampleinfo__species',\
        'team_member_initails__username','date_submitted_for_sequencing',\
        'libraryinfo__library_id','seq_id','libraryinfo__experiment_type',\
        'machine__sequencing_core','machine__machine_name','read_length','read_type',\
        'portion_of_lane','i7index__indexid','i5index__indexid','notes',\
        'seqbioinfo__pipeline_version','seqbioinfo__genome__genome_name',\
        'total_reads','seqbioinfo__final_reads','seqbioinfo__final_yield',\
        'seqbioinfo__mito_frac','seqbioinfo__tss_enrichment','seqbioinfo__frop')
    #print(list(Seqs_list))
    #print(len(Seqs_list))
    rows = Seqs_list
    font_style = xlwt.XFStyle()
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            we.write(row_num, col_num, str((row[col_num] or '')), font_style)
    wb.save(response)
    return response

def SaveAllMetaDataExcel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="AllMetaData.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Samples')
    row_num = 0 
    style = xlwt.XFStyle()
    style.font.bold = True
    style.alignment.wrap = 1
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN    
    pattern.pattern_fore_colour = xlwt.Style.colour_map['turquoise']
    style.pattern = pattern
    borders = xlwt.Borders()
    borders.left = 1
    borders.right = 1
    borders.top = 1
    borders.bottom = 1
    style.borders = borders

    row_num = 0 
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 256*1
    ws.write_merge(0, 0, 0, 20, 'From sample submission form', style)
    style = xlwt.XFStyle()
    style.font.bold = True
    style.alignment.wrap = 1
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN    
    pattern.pattern_fore_colour = xlwt.Style.colour_map['light_green']
    style.pattern = pattern
    borders = xlwt.Borders()
    borders.left = 1
    borders.right = 1
    borders.top = 1
    borders.bottom = 1
    style.borders = borders

    row_num = 0 
    ws.row(row_num).height_mismatch = True
    ws.row(row_num).height = 256*1
    ws.write_merge(0, 0, 21, 24, 'To be entered upon reciept', style)
    row_num = 1
    columns_width = [15,15,15,21,15,15,21,15,25,30,12,15,15,11,12,12,12,12,12,12,30,15,15,15,25]
    columns = ['Date','PI','Research contact name','Research contact e-mail',\
    'Research contact phone','Fiscal contact name','Fiscal conact e-mail','Index for payment',\
    'Sample ID','Sample description','Species','Sample type','Preperation',\
    'Fixation?','Sample amount','Units','Service requested','Sequencing depth to target',\
    'Sequencing length requested','Sequencing type requested', 'Notes',\
    'Date sample received','team member','Storage location','Internal Notes'] 

    for col_num in range(len(columns)):
        ws.col(col_num).width = 256*columns_width[col_num]
        if col_num == 8:
            style = xlwt.XFStyle()
            style.alignment.wrap = 1
            style.font.bold = True
            #first_col = ws.col(0)
            #first_col.width = 256 * 6
            ws.row(row_num).height_mismatch = True
            ws.row(row_num).height = 256*3
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN    
            pattern.pattern_fore_colour = 5
            style.pattern = pattern
            borders = xlwt.Borders()
            borders.left = 1
            borders.right = 1
            borders.top = 1
            borders.bottom = 1
            style.borders = borders
            ws.write(row_num, col_num, columns[col_num], style)

        else:
            style = xlwt.XFStyle()
            style.alignment.wrap = 1
            style.font.bold = True
            #first_col = ws.col(0)
            #first_col.width = 256 * 6
            ws.row(row_num).height_mismatch = True
            ws.row(row_num).height = 256*3
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN    
            pattern.pattern_fore_colour = 22
            style.pattern = pattern
            borders = xlwt.Borders()
            borders.left = 1
            borders.right = 1
            borders.top = 1
            borders.bottom = 1
            style.borders = borders
            ws.write(row_num, col_num, columns[col_num], style)

    Samples_list = SampleInfo.objects.all().order_by('pk').select_related('group',\
        'team_member').values_list('date','group__name',\
        'research_name','research_email','research_phone','fiscal_name','fiscal_email','fiscal_index',\
        'sample_id','description','species','sample_type',\
        'preparation','fixation','sample_amount','unit','service_requested','seq_depth_to_target',\
        'seq_length_requested','seq_type_requested','notes','date_received',\
        'team_member__username','storage','internal_notes'
        )
    #print(list(Samples_list))
    #print(len(Samples_list))
    rows = Samples_list
    font_style = xlwt.XFStyle()
    #rows = User.objects.all().values_list('username', 'first_name', 'last_name', 'email')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str((row[col_num] or '')), font_style)
    wl = wb.add_sheet('Libraries')
    row_num = 0

    columns_width = [30,25,12,15,15,15,20,20,15,30]
    columns = ['Sample ID (Must Match Column I in Sample Sheet)','Library description','Team member intials','Date experiment started','Date experiment completed',\
    'Experiment type','Protocol used','Reference to notebook and page number','library_id',
    'notes'] 
    for col_num in range(len(columns)):
        wl.col(col_num).width = 256*columns_width[col_num]
        if col_num == 0:
            style = xlwt.XFStyle()
            style.alignment.wrap = 1
            style.font.bold = True
            #first_col = ws.col(0)
            #first_col.width = 256 * 6
            wl.row(row_num).height_mismatch = True
            wl.row(row_num).height = 256*3
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN    
            pattern.pattern_fore_colour = 5
            style.pattern = pattern
            borders = xlwt.Borders()
            borders.left = 1
            borders.right = 1
            borders.top = 1
            borders.bottom = 1
            style.borders = borders

        else:
            style = xlwt.XFStyle()
            style.alignment.wrap = 1
            style.font.bold = True
            #first_col = ws.col(0)
            #first_col.width = 256 * 6
            wl.row(row_num).height_mismatch = True
            wl.row(row_num).height = 256*3
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN    
            pattern.pattern_fore_colour = 22
            style.pattern = pattern
            borders = xlwt.Borders()
            borders.left = 1
            borders.right = 1
            borders.top = 1
            borders.bottom = 1
            style.borders = borders
        wl.write(row_num, col_num, columns[col_num], style)
    Libraries_list = LibraryInfo.objects.all().order_by('pk').select_related(\
        'team_member_initails','sampleinfo').values_list('sampleinfo__sample_id',\
        'library_description','team_member_initails__username','date_started',\
        'date_completed','experiment_type','protocal_used',\
        'reference_to_notebook_and_page_number','library_id','notes')
    #print(list(Libraries_list))
    #print(len(Libraries_list))
    rows = Libraries_list
    font_style = xlwt.XFStyle()
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            wl.write(row_num, col_num, str((row[col_num] or '')), font_style)

    we = wb.add_sheet('Sequencings')
    row_num = 0

    columns_width = [30,25,12,12,20,15,15,15,15,15,15,12,10,12,12,30,15,15,15,15,15,15,15,15]
    columns = ['Sample ID (Must Match Column I in Sample Sheet)','Label (for QC report)','Species',\
    'Team member intials','Date submitted for sequencing','Library ID','Sequencing ID','Experiment type',\
    'Sequening core','Machine','Sequening length','Read type','Portion of lane',\
    'i7 index (if applicable)','i5 Index (or single index','Notes','pipeline_version','Genome','total_reads',\
    'final_reads','final_yield','mito_frac','tss_enrichment','frop'] 
    for col_num in range(len(columns)):
        we.col(col_num).width = 256*columns_width[col_num]
        if col_num == 0:
            style = xlwt.XFStyle()
            style.alignment.wrap = 1
            style.font.bold = True
            #first_col = ws.col(0)
            #first_col.width = 256 * 6
            we.row(row_num).height_mismatch = True
            we.row(row_num).height = 256*3
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN    
            pattern.pattern_fore_colour = 5
            style.pattern = pattern
            borders = xlwt.Borders()
            borders.left = 1
            borders.right = 1
            borders.top = 1
            borders.bottom = 1
            style.borders = borders

        else:
            style = xlwt.XFStyle()
            style.alignment.wrap = 1
            style.font.bold = True
            #first_col = ws.col(0)
            #first_col.width = 256 * 6
            we.row(row_num).height_mismatch = True
            we.row(row_num).height = 256*3
            pattern = xlwt.Pattern()
            pattern.pattern = xlwt.Pattern.SOLID_PATTERN    
            pattern.pattern_fore_colour = 22
            style.pattern = pattern
            borders = xlwt.Borders()
            borders.left = 1
            borders.right = 1
            borders.top = 1
            borders.bottom = 1
            style.borders = borders
        we.write(row_num, col_num, columns[col_num], style)
    Seqs_list = SeqInfo.objects.all().order_by('pk').select_related('libraryinfo',\
        'libraryinfo__sampleinfo','team_member_initails','machine','i7index','i5index').\
    prefetch_related(Prefetch('seqbioinfo_set__genome')).values_list(\
        'libraryinfo__sampleinfo__sample_id',\
        'default_label','libraryinfo__sampleinfo__species',\
        'team_member_initails__username','date_submitted_for_sequencing',\
        'libraryinfo__library_id','seq_id','libraryinfo__experiment_type',\
        'machine__sequencing_core','machine__machine_name','read_length','read_type',\
        'portion_of_lane','i7index__indexid','i5index__indexid','notes',\
        'seqbioinfo__pipeline_version','seqbioinfo__genome__genome_name',\
        'total_reads','seqbioinfo__final_reads','seqbioinfo__final_yield',\
        'seqbioinfo__mito_frac','seqbioinfo__tss_enrichment','seqbioinfo__frop')
    #print(list(Seqs_list))
    #print(len(Seqs_list))
    rows = Seqs_list
    font_style = xlwt.XFStyle()
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            we.write(row_num, col_num, str((row[col_num] or '')), font_style)
    wb.save(response)
    return response

# @transaction.atomic
# def SamplesCollabsCreateView(request):
#     samplescollabs_form = SamplesCollabsCreateForm(request.POST or None)
    
#     if samplescollabs_form.is_valid():
#         samplesinfo = samplescollabs_form.cleaned_data['samplesinfo']
#         res = samplescollabs_form.cleaned_data['research_contact']
#         fis = samplescollabs_form.cleaned_data['fiscal_person_index']
#         gname = samplescollabs_form.cleaned_data['group']
#         for sam in samplesinfo.split('\n'):
#             sam = sam.strip()
#             saminfo = SampleInfo.objects.get(sample_id=sam)
#             saminfo.research_person = res
#             saminfo.fiscal_person_index = fis
#             saminfo.group = Group.objects.get(name=gname)
#             saminfo.save()
#         return redirect('masterseq_app:index')

#     context = {
#         'samplescollabs_form':samplescollabs_form,
#     }
#     return render(request, 'masterseq_app/samplescollabsadd.html', context=context)

def load_researchcontact(request):
    groupname = request.GET.get('group')
    researchcontact = CollaboratorPersonInfo.objects.\
    filter(person_id__groups__name__in=[groupname]).prefetch_related(Prefetch('person_id__groups'))
    return render(request, 'masterseq_app/researchcontact_dropdown_list_options.html', {'researchcontact': researchcontact})
      
# def load_fiscalindex(request):
#     groupname = request.GET.get('group')
#     queryset = User.objects.filter(groups__name__in=[groupname])
#     fiscalindex = Person_Index.objects.\
#     filter(person__person_id__groups__name__in=[groupname]).prefetch_related(Prefetch('person__person_id__groups'))
#     return render(request, 'masterseq_app/fiscalindex_dropdown_list_options.html', {'fiscalindex': fiscalindex})

def download(request, path):
    #file_path = os.path.join(settings.MEDIA_ROOT, path)
    dbfolder = os.path.join(os.path.dirname(os.path.dirname(__file__)),'data/masterseq_app')
    file_path = os.path.join(dbfolder,path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404



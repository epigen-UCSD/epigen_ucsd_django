from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SampleCreationForm, LibraryCreationForm, SeqCreationForm,\
    SamplesCreationForm, LibsCreationForm, SeqsCreationForm, SeqsCreationForm,\
    SamplesCollabsCreateForm
from .models import SampleInfo, LibraryInfo, SeqInfo, ProtocalInfo, \
SeqMachineInfo, SeqBioInfo,choice_for_preparation,choice_for_fixation,\
choice_for_unit,choice_for_sample_type
from django.contrib.auth.models import User, Group
from nextseq_app.models import Barcode
from epigen_ucsd_django.shared import datetransform
from django.http import HttpResponse,JsonResponse
from django.db.models import Q
from epigen_ucsd_django.models import CollaboratorPersonInfo,Person_Index
import xlwt
from django.db.models import Prefetch
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


@transaction.atomic
def SamplesCreateView(request):
    sample_form = SamplesCreationForm(request.POST or None)
    tosave_list = []
    data = {}
    if sample_form.is_valid():
        sampleinfo = sample_form.cleaned_data['samplesinfo']
        # print(sequencinginfo)
        for lineitem in sampleinfo.strip().split('\n'):
            fields = lineitem.strip('\n').split('\t')
            samindex = fields[21].strip()
            gname = fields[1].strip() if fields[1].strip() not in ['NA','N/A'] else ''
            if gname:
                group_tm = Group.objects.get(name=gname)
            else:
                group_tm = None
            resname = fields[2].strip() if fields[2].strip() not in ['NA','N/A'] else ''
            resemail = fields[3].strip() if fields[3].strip() not in ['NA','N/A'] else ''
            resphone = fields[4].strip() if fields[4].strip() not in ['NA','N/A'] else ''
            if resname:
                resuser = User.objects.get(first_name=resname.split(' ')[0],last_name=resname.split(' ')[1],email=resemail)
                resperson = CollaboratorPersonInfo.objects.get(person_id=resuser,cell_phone=resphone)
            else:
                resperson = None
            fiscalname = fields[5].strip() if fields[5].strip() not in ['NA','N/A'] else ''
            fiscalemail = fields[6].strip() if fields[6].strip() not in ['NA','N/A'] else ''
            indname = fields[7].strip() if fields[7].strip() not in ['NA','N/A'] else ''
            if fiscalname:
                fisuser = User.objects.get(first_name=fiscalname.split(' ')[0],last_name=fiscalname.split(' ')[1],email=fiscalemail)
                fiscolla = CollaboratorPersonInfo.objects.get(person_id=fisuser)
                fisc_index = Person_Index.objects.get(person=fiscolla,index_name=indname)
            else:
                fisc_index = None

            try:
                samnotes = ';'.join([fields[20].strip(),fields[28].strip()]).strip(';')
            except:
                samnotes = fields[20].strip()           
            try:
                membername = fields[25].strip()
                if membername == '':
                    membername = request.user.username
            except:
                membername = request.user.username
            try:
                storage_tm = fields[26].strip()
            except:
                storage_tm = ''
            service_requested_tm = fields[16].strip()
            seq_depth_to_target_tm = fields[17].strip()
            seq_length_requested_tm = fields[18].strip()
            seq_type_requested_tm = fields[19].strip()
            samprep = fields[12].strip().replace('crypreserant','cryopreservant')
            if samprep not in [x[0].split('(')[0].strip() for x in choice_for_preparation]:
                if samprep.lower().startswith('other'):
                    samprep = 'other (please explain in notes)'
                else:
                    if samprep:
                        samnotes = ';'.join([samnotes,'sample preparation:'+samprep]).strip(';')
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
                date_received = datetransform(fields[23].strip())
            except:
                date_received = None
            data[samid] = {}
            data[samid] = {
                'sample_index': samindex,
                'group':gname,
                'research_person':resname,
                'fiscal_person_index':fiscalname+':'+indname,
                'team_member': membername,
                'date': samdate,
                'date_received':date_received,
                'species': samspecies,
                'sample_type': samtype,
                'preparation': samprep,
                'fixation':fixation,
                'sample_amount':sample_amount,
                'unit':unit,
                'description': samdescript,
                'storage':storage_tm,
                'notes': samnotes,
                'service_requested':service_requested_tm,
                'seq_depth_to_target':seq_depth_to_target_tm,
                'seq_length_requested':seq_length_requested_tm,
                'seq_type_requested':seq_type_requested_tm,
            }
            tosave_item = SampleInfo(
                sample_index=samindex,
                group=group_tm,
                research_person=resperson,
                fiscal_person_index=fisc_index,
                sample_id=samid,
                species=samspecies,
                sample_type=samtype,
                preparation=samprep,
                description=samdescript,
                unit=unit,
                sample_amount=sample_amount,
                fixation=fixation,
                notes=samnotes,
                team_member=User.objects.get(username=membername),
                date=samdate,
                date_received=date_received,
                storage=storage_tm,
                service_requested=service_requested_tm,
                seq_depth_to_target=seq_depth_to_target_tm,
                seq_length_requested=seq_length_requested_tm,
                seq_type_requested=seq_type_requested_tm,
            )
            tosave_list.append(tosave_item)
        if 'Save' in request.POST:
            SampleInfo.objects.bulk_create(tosave_list)
            return redirect('masterseq_app:index')
        if 'Preview' in request.POST:
            displayorder = ['sample_index','group','research_person','fiscal_person_index','description', 'team_member', 'date','date_received','species', 'sample_type',
                            'preparation', 'fixation','sample_amount','unit',
                             'notes','storage','service_requested','seq_depth_to_target',
                            'seq_length_requested','seq_type_requested']
            context = {
                'sample_form': sample_form,
                'modalshow': 1,
                'displayorder': displayorder,
                'data': data,
            }

            return render(request, 'masterseq_app/samplesadd.html', context)
    context = {
        'sample_form': sample_form,
    }

    return render(request, 'masterseq_app/samplesadd.html', context)


@transaction.atomic
def LibrariesCreateView(request):
    library_form = LibsCreationForm(request.POST or None)
    tosave_list = []
    data = {}
    pseudorequired = 0
    if library_form.is_valid():
        libsinfo = library_form.cleaned_data['libsinfo']
        # print(sequencinginfo)
        sampid = {}
        samp_indexes = list(SampleInfo.objects.values_list('sample_index', flat=True))
        existingmaxindex = max([int(x.split('-')[1]) for x in samp_indexes if x.startswith('SAMPNA')])
        for lineitem in libsinfo.strip().split('\n'):
            fields = lineitem.strip('\n').split('\t')
            libid = fields[10].strip()
            sampid = fields[1].strip()
            if fields[0].strip().lower() in ['na','other','n/a']:
                pseudorequired = 1
                pseudoflag = 1
                sampindex = 'SAMPNA-'+str(existingmaxindex+1)              
                existingmaxindex += 1
                if sampid.strip().lower() in ['','na','other','n/a']:
                    sampid = sampindex

            else:
                pseudoflag = 0
                sampindex = fields[0].strip()
                #saminfo = SampleInfo.objects.get(sample_index=fields[0].strip())
        
            data[libid] = {}
            datestart = datetransform(fields[3].strip())
            dateend = datetransform(fields[4].strip())
            libexp = fields[5].strip()
            #libprotocal = ProtocalInfo.objects.get(
                #experiment_type=libexp, protocal_name='other (please explain in notes)')
            refnotebook = fields[7].strip()
            libnote = ';'.join(
                [fields[11].strip(),'Protocol used(recorded in Tracking Sheet 2):', fields[6].strip()]).strip(';')
            #memebername = User.objects.get(username=fields[2].strip())
            data[libid] = {
                'pseudoflag': pseudoflag,
                'sampleinfo': sampindex,
                'sample_index':sampindex,
                'sample_id':sampid,
                'team_member_initails': fields[2].strip(),
                'experiment_index': fields[12].strip(),
                'date_started': datestart,
                'date_completed': dateend,
                'experiment_type': libexp,
                'protocal_name': 'other (please explain in notes)',
                'reference_to_notebook_and_page_number': fields[7].strip(),
                'notes': libnote
            }

        if 'Save' in request.POST:
            for k,v in data.items():
                if v['pseudoflag'] == 1:
                    SampleInfo.objects.create(
                        sample_id=v['sample_id'],
                        sample_index=v['sample_index'],
                        team_member=User.objects.get(username=v['team_member_initails']),
                        )
                tosave_item = LibraryInfo(
                    library_id=k,
                    sampleinfo=SampleInfo.objects.get(sample_index=v['sampleinfo']),
                    experiment_index=v['experiment_index'],
                    experiment_type=v['experiment_type'],
                    protocalinfo=ProtocalInfo.objects.get(experiment_type=v['experiment_type'], protocal_name='other (please explain in notes)'),
                    reference_to_notebook_and_page_number=v['reference_to_notebook_and_page_number'],
                    date_started=v['date_started'],
                    date_completed=v['date_completed'],
                    team_member_initails=User.objects.get(username=v['team_member_initails']),
                    notes=v['notes']
                    )
                tosave_list.append(tosave_item)                
            LibraryInfo.objects.bulk_create(tosave_list)
            return redirect('masterseq_app:index')
        if 'Preview' in request.POST:
            displayorder = ['sampleinfo', 'team_member_initails', 'experiment_index', 'date_started',
                            'date_completed', 'experiment_type', 'protocal_name', 'reference_to_notebook_and_page_number',
                            'notes']
            if pseudorequired == 1:
                displayorder2 = ['sample_index','sample_id','team_member_initails']
                context = {
                    'library_form': library_form,
                    'modalshowplus': 1,
                    'displayorder': displayorder,
                    'displayorder2':displayorder2,
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
    context = {
        'library_form': library_form,
    }

    return render(request, 'masterseq_app/libsadd.html', context)


@transaction.atomic
def SeqsCreateView(request):
    seqs_form = SeqsCreationForm(request.POST or None)
    tosave_list = []
    data = {}
    updatesamprequired = 0
    pseudosamprequired = 0
    pseudolibrequired = 0
    if seqs_form.is_valid():
        seqsinfo = seqs_form.cleaned_data['seqsinfo']
        samp_indexes = list(SampleInfo.objects.values_list('sample_index', flat=True))
        existingmaxsampindex = max([int(x.split('-')[1]) for x in samp_indexes if x.startswith('SAMPNA')])
        lib_indexes = list(LibraryInfo.objects.values_list('experiment_index', flat=True))
        existingmaxlibindex = max([int(x.split('-')[1]) for x in lib_indexes if x.startswith('EXPNA')])

        for lineitem in seqsinfo.strip().split('\n'):
            lineitem = lineitem+'\t\t\t\t\t\t'
            fields = lineitem.split('\t')
            updatesampflag = 0
            pseudolibflag = 0 
            pseudosamflag = 0
            samindex = fields[0].strip()
            sampid = fields[1].strip()
            sampspecies = fields[3].strip().lower()
            seqid = fields[8].strip()
            expindex = fields[4].strip()
            libraryid = fields[7].strip()
            exptype = fields[9].strip()
            data[seqid] = {}
            if not LibraryInfo.objects.filter(library_id=fields[7]).exists() and expindex.strip().lower() in ['','na','other','n/a']:
                pseudolibrequired = 1
                pseudolibflag = 1
                expindex = 'EXPNA-'+str(existingmaxlibindex+1)
                existingmaxlibindex += 1
                if not SampleInfo.objects.filter(sample_index=samindex).exists() and samindex.strip().lower() in ['na','other','n/a']:
                    pseudosamprequired = 1
                    pseudosamflag = 1
                    sampindex = 'SAMPNA-'+str(existingmaxsampindex+1)              
                    existingmaxsampindex += 1 
                    if sampid.strip().lower() in ['','na','other','n/a']:
                        sampid = sampindex
                else:
                    sampinfo = SampleInfo.objects.get(sample_index=samindex)
                    if not sampinfo.species and sampspecies:
                        updatesampflag = 1
                        updatesamprequired  = 1
            else:
                libinfo = LibraryInfo.objects.select_related('sampleinfo').get(library_id=fields[7].strip())
                sampinfo = libinfo.sampleinfo
                sampindex = sampinfo.sample_index
                sampid = sampinfo.sample_id
                
                if not sampinfo.species and sampspecies:
                    updatesampflag = 1
                    updatesamprequired  = 1
            
            if '-' in fields[6].strip():
                datesub = fields[6].strip()
            else:
                datesub = datetransform(fields[6].strip())
            memebername = User.objects.get(username=fields[5].strip())
            indexname = fields[15].strip()
            if indexname and indexname not in ['NA', 'Other (please explain in notes)', 'N/A']:
                i7index = Barcode.objects.get(indexid=indexname)
            else:
                i7index = None
            indexname2 = fields[16].strip()
            if indexname2 and indexname2 not in ['NA', 'Other (please explain in notes)', 'N/A']:
                i5index = Barcode.objects.get(indexid=indexname2)
            else:
                i5index = None
            polane = fields[14].strip()
            if polane and polane not in ['NA', 'Other (please explain in notes)', 'N/A']:
                polane = float(polane)
            else:
                polane = None
            seqid = fields[8].strip()
            seqcore = fields[10].split('(')[0].strip()
            seqmachine = fields[11].split('(')[0].strip()
            machineused = SeqMachineInfo.objects.get(
                sequencing_core=seqcore, machine_name=seqmachine)
            data[seqid] = {
                'updatesampflag':updatesampflag,
                'pseudolibflag':pseudolibflag,
                'pseudosamflag':pseudosamflag,
                'sample_index':sampindex,
                'sampleinfo':sampindex,
                'sample_id':sampid,
                'species':sampspecies,
                'experiment_index':expindex,
                'experiment_type':exptype,
                'libraryinfo': fields[7].strip(),
                'library_id':libraryid,
                'default_label': fields[2].strip(),
                'team_member_initails': fields[5].strip(),
                'read_length': fields[12].strip(),
                'read_type': fields[13].strip(),
                'portion_of_lane': polane,
                'seqcore': fields[10].split('(')[0].strip(),
                'machine': seqmachine,
                'i7index': indexname,
                'i5index': indexname2,
                'indexname':indexname,
                'indexname2':indexname2,
                'date_submitted': datesub,
                'notes': fields[17].strip(),
            }
        if 'Save' in request.POST:           
            
            for k,v in data.items():
                if v['pseudolibflag'] == 1:
                    if v['pseudosamflag'] == 1:
                        SampleInfo.objects.create(
                            sample_id=v['sample_id'],
                            sample_index=v['sample_index'],
                            species=v['species'],
                            team_member=User.objects.get(username=v['team_member_initails']),
                            )

                    LibraryInfo.objects.create(
                        library_id=v['library_id'],
                        experiment_index=v['experiment_index'],
                        experiment_type=v['experiment_type'],
                        sampleinfo=SampleInfo.objects.get(sample_index=v['sample_index']),
                        team_member_initails=User.objects.get(username=v['team_member_initails']),
                            )
                if v['updatesampflag'] == 1:
                    sampleinfo = SampleInfo.objects.get(sample_index=v['sample_index'])
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
                    libraryinfo=LibraryInfo.objects.get(library_id=v['library_id']),
                    team_member_initails=User.objects.get(username=v['team_member_initails']),
                    read_length=v['read_length'],
                    read_type=v['read_type'],
                    portion_of_lane=v['portion_of_lane'],
                    notes=v['notes'],
                    machine=SeqMachineInfo.objects.get(sequencing_core=v['seqcore'], machine_name=v['machine']),
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
            displayorder2 = ['sample_index','sample_id','species','team_member_initails']
            displayorder3 = ['library_id','sampleinfo','experiment_index','experiment_type','team_member_initails']
            context = {
                    'updatesamprequired':updatesamprequired,
                    'pseudosamprequired':pseudosamprequired,
                    'pseudolibrequired':pseudolibrequired,
                    'seqs_form': seqs_form,
                    'modalshowplus': 1,
                    'displayorder': displayorder,
                    'displayorder2':displayorder2,
                    'displayorder3':displayorder3,
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
        'pk', 'sample_id', 'description','date', 'sample_type', 'group__name', 'status')
    for sample in Samples_list:
        try:
            sample['group__name'] = sample['group__name'].replace(
                '_group', '').replace('_', ' ')
        except:
            pass
    data = list(Samples_list)

    return JsonResponse(data, safe=False)


def LibDataView(request):
    Libs_list = LibraryInfo.objects.all().values(
        'pk', 'library_id', 'date_started', 'date_completed', 'experiment_type')
    data = list(Libs_list)

    return JsonResponse(data, safe=False)


def SeqDataView(request):
    Seqs_list = SeqInfo.objects.all().values(
        'pk', 'seq_id', 'date_submitted_for_sequencing', 'read_length', 'read_type')
    data = list(Seqs_list)

    return JsonResponse(data, safe=False)


def UserSampleDataView(request):
    Samples_list = SampleInfo.objects.filter(team_member=request.user).values(
        'pk', 'sample_id', 'description','date', 'sample_type', 'group__name', 'status')
    for sample in Samples_list:
        try:
            sample['group__name'] = sample['group__name'].replace(
                '_group', '').replace('_', ' ')
        except:
            pass
    data = list(Samples_list)

    return JsonResponse(data, safe=False)


def UserLibDataView(request):
    Libs_list = LibraryInfo.objects.filter(team_member_initails=request.user).values(
        'pk', 'library_id', 'date_started', 'date_completed', 'experiment_type')
    data = list(Libs_list)

    return JsonResponse(data, safe=False)


def UserSeqDataView(request):
    Seqs_list = SeqInfo.objects.filter(team_member_initails=request.user).values(
        'pk', 'seq_id', 'date_submitted_for_sequencing', 'read_length', 'read_type')
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
    summaryfield = ['status', 'sample_index', 'sample_id','description', 'date','date_received','team_member', 'species',
                    'sample_type', 'preparation', 'fixation', 'sample_amount', 'unit', 'storage', 'notes']
    requestedfield = ['date', 'service_requested', 'seq_depth_to_target',
                      'seq_length_requested', 'seq_type_requested']
    libfield = ['library_id', 'experiment_type',
                'protocalinfo', 'reference_to_notebook_and_page_number']
    seqfield = ['seq_id', 'default_label', 'machine',
                'read_length', 'read_type', 'total_reads']
    libinfo = sampleinfo.libraryinfo_set.all().select_related('protocalinfo')
    seqs = SeqInfo.objects.none()
    for lib in libinfo:
        seqinfo = lib.seqinfo_set.all().select_related('machine')
        seqs = seqs | seqinfo
    try:
        researchperson = sampleinfo.research_person.person_id
        researchperson_phone = sampleinfo.research_person.cell_phone
    except:
        researchperson = ''
        researchperson_phone = ''
    try:
        fiscalperson = sampleinfo.fiscal_person_index.person.person_id
        fiscalperson_phone = sampleinfo.fiscal_person_index.person.cell_phone
        index = sampleinfo.fiscal_person_index.index_name
    except:
        fiscalperson = ''
        fiscalperson_phone = ''
        index = ''
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
        'researchperson': researchperson,
        'researchperson_phone': researchperson_phone,
        'index': index,
        'fiscalperson': fiscalperson,
        'fiscalperson_phone': fiscalperson_phone,
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
    summaryfield = ['library_id', 'sampleinfo', 'date_started', 'date_completed',
                    'team_member_initails', 'experiment_type', 'protocalinfo',
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
    summaryfield = ['seq_id', 'sampleinfo','libraryinfo', 'default_label', 'team_member_initails',
                    'date_submitted_for_sequencing', 'machine', 'read_length', 'read_type', 'portion_of_lane',
                    'i7index', 'i5index', 'total_reads', 'notes']
    bioinfofield = ['genome', 'pipeline_version', 'final_reads', 'final_yield', 'mito_frac',
                    'tss_enrichment', 'frop']
    seqbioinfos = seqinfo.seqbioinfo_set.all().select_related('genome')
    context = {
        'libinfo': libinfo,
        'saminfo':saminfo,
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
    summaryfield = ['seq_id','sampleinfo', 'libraryinfo', 'default_label', 'team_member_initails',
                    'date_submitted_for_sequencing', 'machine', 'read_length', 'read_type', 'portion_of_lane',
                    'i7index', 'i5index', 'total_reads', 'notes']
    bioinfofield = ['genome', 'pipeline_version', 'final_reads', 'final_yield', 'mito_frac',
                    'tss_enrichment', 'frop']
    seqbioinfos = seqinfo.seqbioinfo_set.all().select_related('genome')
    context = {
        'libinfo': libinfo,
        'saminfo':saminfo,
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
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Date','Group','PI','Research contact name','Research contact e-mail',\
    'Research contact phone','Fiscal contact name','Fiscal conact e-mail','Index for payment',\
    'Sample ID','Sample description','Species','Sample type','Preperation',\
    'Fixation?','Sample amount','Units','Service requested','Sequencing depth to target',\
    'Sequencing length requested','Sequencing type requested', 'Notes','Sample Index',\
    'Date sample received','team member','Storage location','status'] 
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    Samples_list = SampleInfo.objects.filter(team_member=request.user).order_by('pk').select_related('research_person__person_id','group','team_member',\
        'fiscal_person_index__person__person_id').values_list('date','group__name',\
        'research_person__person_id__first_name','research_person__person_id__last_name',\
        'research_person__person_id__email','research_person__cell_phone',
        'fiscal_person_index__person__person_id__first_name','fiscal_person_index__person__person_id__last_name',\
        'fiscal_person_index__person__person_id__email',\
        'fiscal_person_index__index_name','sample_id','description','species','sample_type',\
        'preparation','fixation','sample_amount','unit','service_requested','seq_depth_to_target',\
        'seq_length_requested','seq_type_requested','notes','sample_index','date_received',\
        'team_member__username','storage','status'
        )
    #print(list(Samples_list))
    #print(len(Samples_list))
    rows = Samples_list
    font_style = xlwt.XFStyle()
    #rows = User.objects.all().values_list('username', 'first_name', 'last_name', 'email')
    for row in rows:
        row_num += 1
        for col_num in range(0,2):
            ws.write(row_num, col_num, str((row[col_num] or '')), font_style)
        ws.write(row_num, 2, '', font_style)
        ws.write(row_num, 3, (row[2] or '')+' '+(row[3] or ''), font_style)
        for col_num in range(4,6):
            ws.write(row_num, col_num, (row[col_num] or ''), font_style)
        ws.write(row_num, 6, (row[6] or '')+' '+(row[7] or ''), font_style)
        for col_num in range(7,len(row)-1):
            ws.write(row_num, col_num, str((row[col_num+1] or '')), font_style)
    wl = wb.add_sheet('Libraries')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Sample Index','Sample id','team member','date_started','date_completed',\
    'experiment_type','protocal used','reference_to_notebook_and_page_number','library_id',
    'notes','experiment_index'] 
    for col_num in range(len(columns)):
        wl.write(row_num, col_num, columns[col_num], font_style)
    Libraries_list = LibraryInfo.objects.filter(team_member_initails=request.user).order_by('pk').select_related('protocalinfo',\
        'team_member_initails','sampleinfo').values_list('sampleinfo__sample_index',\
        'sampleinfo__sample_id','team_member_initails__username','date_started',\
        'date_completed','experiment_type','protocalinfo__protocal_name',\
        'reference_to_notebook_and_page_number','library_id','notes','experiment_index')
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
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Sample Index','Sample id','Label','Species','Experiment Index',\
    'Team Member','date_submitted_for_sequencing','library_id','seq_id','experiment_type',\
    'sequencing_core','machine','read_length','read_type','portion_of_lane',\
    'i7index','i5index','notes','pipeline_version','Genome','total_reads',\
    'final_reads','final_yield','mito_frac','tss_enrichment','frop'] 
    for col_num in range(len(columns)):
        we.write(row_num, col_num, columns[col_num], font_style)
    Seqs_list = SeqInfo.objects.filter(team_member_initails=request.user).order_by('pk').select_related('libraryinfo',\
        'libraryinfo__sampleinfo','team_member_initails','machine','i7index','i5index').\
    prefetch_related(Prefetch('seqbioinfo_set__genome')).values_list(\
        'libraryinfo__sampleinfo__sample_index','libraryinfo__sampleinfo__sample_id',\
        'default_label','libraryinfo__sampleinfo__species','libraryinfo__experiment_index',\
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
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Date','Group','PI','Research contact name','Research contact e-mail',\
    'Research contact phone','Fiscal contact name','Fiscal conact e-mail','Index for payment',\
    'Sample ID','Sample description','Species','Sample type','Preperation',\
    'Fixation?','Sample amount','Units','Service requested','Sequencing depth to target',\
    'Sequencing length requested','Sequencing type requested', 'Notes','Sample Index',\
    'Date sample received','team member','Storage location','status'] 
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    Samples_list = SampleInfo.objects.all().order_by('pk').select_related('research_person__person_id','group','team_member',\
        'fiscal_person_index__person__person_id').values_list('date','group__name',\
        'research_person__person_id__first_name','research_person__person_id__last_name',\
        'research_person__person_id__email','research_person__cell_phone',
        'fiscal_person_index__person__person_id__first_name','fiscal_person_index__person__person_id__last_name',\
        'fiscal_person_index__person__person_id__email',\
        'fiscal_person_index__index_name','sample_id','description','species','sample_type',\
        'preparation','fixation','sample_amount','unit','service_requested','seq_depth_to_target',\
        'seq_length_requested','seq_type_requested','notes','sample_index','date_received',\
        'team_member__username','storage','status'
        )
    #print(list(Samples_list))
    #print(len(Samples_list))
    rows = Samples_list
    font_style = xlwt.XFStyle()
    #rows = User.objects.all().values_list('username', 'first_name', 'last_name', 'email')
    for row in rows:
        row_num += 1
        for col_num in range(0,2):
            ws.write(row_num, col_num, str((row[col_num] or '')), font_style)
        ws.write(row_num, 2, '', font_style)
        ws.write(row_num, 3, (row[2] or '')+' '+(row[3] or ''), font_style)
        for col_num in range(4,6):
            ws.write(row_num, col_num, (row[col_num] or ''), font_style)
        ws.write(row_num, 6, (row[6] or '')+' '+(row[7] or ''), font_style)
        for col_num in range(7,len(row)-1):
            ws.write(row_num, col_num, str((row[col_num+1] or '')), font_style)
    wl = wb.add_sheet('Libraries')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Sample Index','Sample id','team member','date_started','date_completed',\
    'experiment_type','protocal used','reference_to_notebook_and_page_number','library_id',
    'notes','experiment_index'] 
    for col_num in range(len(columns)):
        wl.write(row_num, col_num, columns[col_num], font_style)
    Libraries_list = LibraryInfo.objects.all().order_by('pk').select_related('protocalinfo',\
        'team_member_initails','sampleinfo').values_list('sampleinfo__sample_index',\
        'sampleinfo__sample_id','team_member_initails__username','date_started',\
        'date_completed','experiment_type','protocalinfo__protocal_name',\
        'reference_to_notebook_and_page_number','library_id','notes','experiment_index')
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
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Sample Index','Sample id','Label','Species','Experiment Index',\
    'Team Member','date_submitted_for_sequencing','library_id','seq_id','experiment_type',\
    'sequencing_core','machine','read_length','read_type','portion_of_lane',\
    'i7index','i5index','notes','pipeline_version','Genome','total_reads',\
    'final_reads','final_yield','mito_frac','tss_enrichment','frop'] 
    for col_num in range(len(columns)):
        we.write(row_num, col_num, columns[col_num], font_style)
    Seqs_list = SeqInfo.objects.all().order_by('pk').select_related('libraryinfo',\
        'libraryinfo__sampleinfo','team_member_initails','machine','i7index','i5index').\
    prefetch_related(Prefetch('seqbioinfo_set__genome')).values_list(\
        'libraryinfo__sampleinfo__sample_index','libraryinfo__sampleinfo__sample_id',\
        'default_label','libraryinfo__sampleinfo__species','libraryinfo__experiment_index',\
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

@transaction.atomic
def SamplesCollabsCreateView(request):
    samplescollabs_form = SamplesCollabsCreateForm(request.POST or None)
    
    if samplescollabs_form.is_valid():
        samplesinfo = samplescollabs_form.cleaned_data['samplesinfo']
        res = samplescollabs_form.cleaned_data['research_contact']
        fis = samplescollabs_form.cleaned_data['fiscal_person_index']
        gname = samplescollabs_form.cleaned_data['group']
        for sam in samplesinfo.split('\n'):
            sam = sam.strip()
            saminfo = SampleInfo.objects.get(sample_id=sam)
            saminfo.research_person = res
            saminfo.fiscal_person_index = fis
            saminfo.group = Group.objects.get(name=gname)
            saminfo.save()
        return redirect('masterseq_app:index')

    context = {
        'samplescollabs_form':samplescollabs_form,
    }
    return render(request, 'masterseq_app/samplescollabsadd.html', context=context)

def load_researchcontact(request):
    groupname = request.GET.get('group')
    researchcontact = CollaboratorPersonInfo.objects.\
    filter(person_id__groups__name__in=[groupname]).prefetch_related(Prefetch('person_id__groups'))
    return render(request, 'masterseq_app/researchcontact_dropdown_list_options.html', {'researchcontact': researchcontact})
      
def load_fiscalindex(request):
    groupname = request.GET.get('group')
    queryset = User.objects.filter(groups__name__in=[groupname])
    fiscalindex = Person_Index.objects.\
    filter(person__person_id__groups__name__in=[groupname]).prefetch_related(Prefetch('person__person_id__groups'))
    return render(request, 'masterseq_app/fiscalindex_dropdown_list_options.html', {'fiscalindex': fiscalindex})
 
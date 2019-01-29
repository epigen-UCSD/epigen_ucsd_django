from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SampleCreationForm, LibraryCreationForm, SeqCreationForm,\
    SamplesCreationForm, LibsCreationForm, SeqsCreationForm, SeqsCreationForm
from .models import SampleInfo, LibraryInfo, SeqInfo, ProtocalInfo, SeqMachineInfo, SeqBioInfo
from django.contrib.auth.models import User, Group
from nextseq_app.models import Barcode
from epigen_ucsd_django.shared import datetransform
from django.http import JsonResponse
from django.db.models import Q
from epigen_ucsd_django.models import CollaboratorPersonInfo
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
            samnotes = fields[20].strip()
            samprep = fields[12].split('(')[0].strip()
            if samprep == 'other':
                samprep = 'other (please explain in notes)'
            samtype = fields[11].split('(')[0].strip()
            samspecies = fields[10].split('(')[0].lower().strip()
            samdescript = fields[9].strip()
            samid = fields[8].strip()
            data[samid] = {}
            samdate = datetransform(fields[0].strip())
            data[samid] = {
                'sample_index': samindex,
                'team_member': request.user.username,
                'date': samdate,
                'species': samspecies,
                'sample_type': samtype,
                'preparation': samprep,
                'description': samdescript,
                'notes': samnotes
            }
            tosave_item = SampleInfo(
                sample_index=samindex,
                sample_id=samid,
                species=samspecies,
                sample_type=samtype,
                preparation=samprep,
                description=samdescript,
                notes=samnotes,
                team_member=request.user,
                date=samdate,
            )
            tosave_list.append(tosave_item)
        if 'Save' in request.POST:
            SampleInfo.objects.bulk_create(tosave_list)
            return redirect('masterseq_app:index')
        if 'Preview' in request.POST:
            displayorder = ['sample_index', 'team_member', 'date', 'species', 'sample_type',
                            'preparation', 'description', 'notes']
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
                [fields[11].strip(), fields[6].strip()]).strip(';')
            #memebername = User.objects.get(username=fields[2].strip())
            data[libid] = {
                'pseudoflag': pseudoflag,
                'sampleinfo': sampindex,
                'sampid':sampid,
                'team_member_initails': fields[2].strip(),
                'experiment_index': fields[12].strip(),
                'date_started': datestart,
                'date_completed': dateend,
                'experiment_type': libexp,
                'protocal_name': 'other (please explain in notes)',
                'reference_to_notebook_and_page_number': fields[7].strip(),
                'notes': libnote
            }
            print(datestart)
            print(dateend)

        if 'Save' in request.POST:
            for k,v in data.items():
                if v['pseudoflag'] == 1:
                    SampleInfo.objects.create(
                        sample_id=v['sampid'],
                        sample_index=v['sampleinfo']
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
                displayorder2 = ['sampleinfo','sampid']
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
    if seqs_form.is_valid():
        seqsinfo = seqs_form.cleaned_data['seqsinfo']
        for lineitem in seqsinfo.strip().split('\n'):
            lineitem = lineitem+'\t\t\t\t\t\t'
            fields = lineitem.split('\t')
            seqid = fields[8].strip()
            exptype = fields[9].strip()
            data[seqid] = {}
            libinfo = LibraryInfo.objects.get(library_id=fields[7].strip())
            if '-' in fields[6].strip():
                datesub = fields[6].strip()
            else:
                datesub = datetransform(fields[6].strip())
            memebername = User.objects.get(username=fields[5].strip())
            indexname = fields[15].strip()
            if indexname and indexname not in ['NA', 'Other (please explain in notes)', 'N/A'] and exptype not in ['scATAC-seq', 'snATAC-seq']:
                i7index = Barcode.objects.get(indexid=indexname)
            else:
                i7index = None
            indexname2 = fields[16].strip()
            if indexname2 and indexname2 not in ['NA', 'Other (please explain in notes)', 'N/A'] and exptype not in ['scATAC-seq', 'snATAC-seq']:
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
                'libraryinfo': fields[7].strip(),
                'default_label': fields[2].strip(),
                'team_member_initails': fields[5].strip(),
                'read_length': fields[12].strip(),
                'read_type': fields[13].strip(),
                'portion_of_lane': fields[14].strip(),
                'seqcore': fields[10].split('(')[0].strip(),
                'machine': seqmachine,
                'i7index': indexname,
                'i5index': indexname2,
                'date_submitted': datesub,
                'notes': fields[17].strip(),
            }
            tosave_item = SeqInfo(
                seq_id=seqid,
                libraryinfo=libinfo,
                team_member_initails=memebername,
                read_length=fields[12].strip(),
                read_type=fields[13].strip(),
                portion_of_lane=polane,
                notes=fields[17].strip(),
                machine=machineused,
                i7index=i7index,
                i5index=i5index,
                default_label=fields[2].strip(),
                date_submitted_for_sequencing=datesub,
            )
            tosave_list.append(tosave_item)
        if 'Save' in request.POST:
            SeqInfo.objects.bulk_create(tosave_list)
            return redirect('masterseq_app:index')
        if 'Preview' in request.POST:
            displayorder = ['libraryinfo', 'default_label', 'date_submitted', 'team_member_initails', 'read_length',
                            'read_type', 'portion_of_lane', 'seqcore', 'machine', 'i7index', 'i5index', 'notes']
            context = {
                'seqs_form': seqs_form,
                'modalshow': 1,
                'displayorder': displayorder,
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
        'pk', 'sample_id', 'date', 'sample_type', 'service_requested', 'group__name', 'status')
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
        'pk', 'sample_id', 'date', 'sample_type', 'service_requested', 'group__name', 'status')
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
    summaryfield = ['status', 'sample_index', 'sample_id', 'team_member', 'species',
                    'sample_type', 'preparation', 'fixation', 'sample_amount', 'unit', 'description', 'notes']
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
        fiscalperson = sampleinfo.fiscal_person.person_id
        fiscalperson_phone = sampleinfo.fiscal_person.cell_phone
        index = sampleinfo.fiscal_person.fiscal_index
    except:
        fiscalperson = ''
        fiscalperson_phone = ''
        index = ''
    groupinfo = []
    piname = []
    piemail = []
    if researchperson:
        for group in researchperson.groups.all():
            groupinfo.append(group.name)
            for user in group.user_set.all():
                for person in user.collaboratorpersoninfo_set.all():
                    if 'PI' in person.role:
                        piname.append(user.first_name + ' ' + user.last_name)

    context = {
        'groupinfo': ';'.join(groupinfo),
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
    summaryfield = ['seq_id', 'libraryinfo', 'default_label', 'team_member_initails',
                    'date_submitted_for_sequencing', 'machine', 'read_length', 'read_type', 'portion_of_lane',
                    'i7index', 'i5index', 'total_reads', 'notes']
    bioinfofield = ['genome', 'pipeline_version', 'final_reads', 'final_yield', 'mito_frac',
                    'tss_enrichment', 'frop']
    seqbioinfos = seqinfo.seqbioinfo_set.all().select_related('genome')
    context = {
        'libinfo': libinfo,
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
    summaryfield = ['seq_id', 'libraryinfo', 'default_label', 'team_member_initails',
                    'date_submitted_for_sequencing', 'machine', 'read_length', 'read_type', 'portion_of_lane',
                    'i7index', 'i5index', 'total_reads', 'notes']
    bioinfofield = ['genome', 'pipeline_version', 'final_reads', 'final_yield', 'mito_frac',
                    'tss_enrichment', 'frop']
    seqbioinfos = seqinfo.seqbioinfo_set.all().select_related('genome')
    context = {
        'libinfo': libinfo,
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

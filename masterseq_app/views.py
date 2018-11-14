from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SampleCreationForm,LibraryCreationForm,SeqCreationForm,\
SamplesCreationForm,LibsCreationForm
from .models import SampleInfo,LibraryInfo,SeqInfo,ProtocalInfo
from django.contrib.auth.models import User
from nextseq_app.models import Barcode
from epigen_ucsd_django.shared import datetransform
# Create your views here.
@transaction.atomic
def SampleCreateView(request):
    sample_form = SampleCreationForm(request.POST or None)
    if sample_form.is_valid():
        sampleinfo = sample_form.save(commit=False)
        sampleinfo.team_member = request.user
        sampleindexs = list(SampleInfo.objects.values_list('sample_index', flat=True))
        if not sampleindexs:
            sampleinfo.sample_index = 'SAMP-2000'
        else:
            maxid = max([int(x.split('-')[1]) for x in sampleindexs if x.startswith('SAMP-')])
            sampleinfo.sample_index = '-'.join(['SAMP',str(maxid+1)])
        sampleinfo.save()
        return redirect('masterseq_app:index')
    context = {
        'sample_form': sample_form,
    }

    return render(request, 'masterseq_app/sampleadd.html', context)

@transaction.atomic
def LibraryCreateView(request):
    library_form = LibraryCreationForm(request.POST or None)
    if library_form.is_valid():
        librayinfo = library_form.save(commit=False)
        librayinfo.team_member_initails = request.user
        expindexs = list(LibraryInfo.objects.values_list('experiment_index', flat=True))
        if not expindexs:
            librayinfo.experiment_index = 'EXP-2000'
        else:
            maxid = max([int(x.split('-')[1]) for x in expindexs if x.startswith('EXP-')])
            librayinfo.experiment_index = '-'.join(['EXP',str(maxid+1)])
        librayinfo.save()
        return redirect('masterseq_app:index')
    context = {
        'library_form': library_form,
    }

    return render(request, 'masterseq_app/libraryadd.html', context)

@transaction.atomic
def SeqCreateView(request):
    seq_form = SeqCreationForm(request.POST or None)
    tosave_list = []
    if seq_form.is_valid():
        readlen = seq_form.cleaned_data['read_length']
        machine = seq_form.cleaned_data['machine']
        readtype = seq_form.cleaned_data['read_type']
        date = seq_form.cleaned_data['date_submitted_for_sequencing']
        sequencinginfo = seq_form.cleaned_data['sequencinginfo']
        #print(sequencinginfo)
        for lineitem in sequencinginfo.strip().split('\n'):
            if not lineitem.startswith('SeqID\tLibID') and lineitem != '\r':
                fields = lineitem.strip('\n').split('\t')
                seqid = fields[0]
                libid = LibraryInfo.objects.get(library_id=fields[1])
                dflabel = fields[2]
                tmem = User.objects.get(username=fields[3])
                if fields[4]:
                    polane = float(fields[4])
                else:
                    polane = None
                if fields[5]:
                    i7index = Barcode.objects.get(indexid=fields[5])
                else:
                    i7index = None
                if fields[6]:
                    i5index = Barcode.objects.get(indexid=fields[5])
                else:
                    i5index = None
                if fields[7]:
                    notes = fields[7]
                else:
                    notes = ''
                tosave_item = SeqInfo(
                    seq_id = seqid,
                    libraryinfo = libid,
                    team_member_initails = tmem,
                    machine = machine,
                    read_length = readlen,
                    read_type = readtype,
                    portion_of_lane = polane,
                    i7index = i7index,
                    i5index = i5index,
                    date_submitted_for_sequencing = date,
                    default_label = dflabel,
                    notes = notes
                    )
                tosave_list.append(tosave_item)
        SeqInfo.objects.bulk_create(tosave_list)
        return redirect('masterseq_app:index')
    context = {
        'seq_form': seq_form,
    }

    return render(request, 'masterseq_app/seqadd.html', context)



def load_protocals(request):
    exptype = request.GET.get('exptype')
    protocals = ProtocalInfo.objects.filter(experiment_type=exptype).order_by('protocal_name')
    print(protocals)
    return render(request, 'masterseq_app/protocal_dropdown_list_options.html', {'protocals': protocals})

@transaction.atomic
def SamplesCreateView(request):
    sample_form = SamplesCreationForm(request.POST or None)
    tosave_list = []
    if sample_form.is_valid():
        sampleinfo = sample_form.cleaned_data['samplesinfo']
        #print(sequencinginfo)
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
            samdate = datetransform(fields[0].strip())

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
        SampleInfo.objects.bulk_create(tosave_list)
        return redirect('masterseq_app:index')
    context = {
        'sample_form': sample_form,
    }

    return render(request, 'masterseq_app/samplesadd.html', context)
@transaction.atomic
def LibrariesCreateView(request):
    library_form = LibsCreationForm(request.POST or None)
    tosave_list = []
    if library_form.is_valid():
        libsinfo = library_form.cleaned_data['libsinfo']
        #print(sequencinginfo)
        for lineitem in libsinfo.strip().split('\n'):
            fields = lineitem.strip('\n').split('\t')
            saminfo = SampleInfo.objects.get(sample_index=fields[0].strip())
            libid = fields[10].strip()
            datestart = datetransform(fields[3].strip())
            dateend = datetransform(fields[4].strip())
            libexp = fields[5].strip()
            libprotocal = ProtocalInfo.objects.get(experiment_type=libexp,protocal_name = 'other (please explain in notes)')   
            refnotebook = fields[7].strip()
            libnote = ';'.join([fields[11].strip(),fields[6].strip()]).strip(';')
            tosave_item = LibraryInfo(
                library_id=libid,
                sampleinfo=saminfo,
                experiment_index=fields[12].strip(),
                experiment_type=libexp,
                protocalinfo=libprotocal,
                reference_to_notebook_and_page_number=refnotebook,
                date_started=datestart,
                date_completed=dateend,
                team_member_initails=request.user,
                notes=libnote
                )
            tosave_list.append(tosave_item)
        LibraryInfo.objects.bulk_create(tosave_list)
        return redirect('masterseq_app:index')
    context = {
        'library_form': library_form,
    }

    return render(request, 'masterseq_app/libsadd.html', context)

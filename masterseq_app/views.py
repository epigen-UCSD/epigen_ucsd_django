from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SampleCreationForm,LibraryCreationForm,SeqCreationForm
from .models import SampleInfo,LibraryInfo,SeqInfo
from django.contrib.auth.models import User
from nextseq_app.models import Barcode
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


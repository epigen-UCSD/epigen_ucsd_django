from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SampleCreationForm,LibraryCreationForm
from .models import SampleInfo,LibraryInfo
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





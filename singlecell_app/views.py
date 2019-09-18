from django.shortcuts import render
from masterseq_app.models import LibraryInfo
# Create your views here.
def scIndex(request):
    library_list = LibraryInfo.objects.filter(team_member_initails=request.user,
     experiment_type='10xATAC')
    
    lib_ids = list(library_list.values_list('library_id', flat=True))
    
    context = {
        'type' : 'My Single Cell Libraries',
        'lib_ids' : lib_ids
    }
    return render(request, 'singlecell_app/scIndex.html', context)

def AllScLibs(request):
    library_list = LibraryInfo.objects.filter(experiment_type='10xATAC')
    lib_ids = list(library_list.values_list('library_id', flat=True))
    context = {
        'type': 'All Single Cell Libraries',
        'lib_ids': lib_ids
    }
    return render(request, 'singlecell_app/scIndex.html', context)
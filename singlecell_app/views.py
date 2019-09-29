from django.shortcuts import render
from masterseq_app.models import LibraryInfo
# Create your views here.

'''
To add a column to scIndex or AllScLibs of libraryModel info, simply add the title of the coloumn wanted and the field name into a tuple
in header
list, eg ('Title of column', 'field_name')
'''

#hold all single cell experiment values
SINGLE_CELL_EXPS = ['10xATAC','scRNA-seq','snRNA-seq', 'scATAC-seq']

def scIndex(request):    
    #library_list = LibraryInfo.objects.filter(experiment_type='10xATAC').order_by('-date_started')
    library_list = LibraryInfo.objects.filter(experiment_type__in=SINGLE_CELL_EXPS, team_member_initails=request.user).values().order_by('-date_started')
    print('lib list: ', library_list)
    header = [
        ('Library ID', 'library_id'),
        ('Library Description', 'library_description'),
        ('Sample Info', 'sampleinfo_id'),
        ('Experiment Type','experiment_type'),
        ('Date Started' ,'date_started'),
        ('Date Completed' ,'date_completed'),
    ]

    library_lists = BuildLibraryList(library_list, header)
    print(library_lists)
    context = {
        'type' : 'My Single Cell Libraries',
        'header' : header,
        'library_lists': library_lists,
    }
    return render(request, 'singlecell_app/scIndex.html', context)

def AllScLibs(request):
    #library_list = LibraryInfo.objects.filter(experiment_type='10xATAC').order_by('-date_started')
    library_list = LibraryInfo.objects.select_related('User').filter(experiment_type__in=SINGLE_CELL_EXPS).values().order_by('-date_started')
    print('lib list: ', library_list)
    header = [
        ('Library ID', 'library_id'),
        ('Library Description', 'library_description') ,
        ('Sample Info', 'sampleinfo_id'),
        ('Experiment Type','experiment_type'),
        ('Date Started' ,'date_started'),
        ('Date Completed' ,'date_completed'),
    ]
    library_lists = BuildLibraryList(library_list, header)
    print(library_lists)
    context = {
        'type' : 'All Single Cell Libraries',
        'header' : header,
        'library_lists': library_lists,
    }
    return render(request, 'singlecell_app/scIndex.html', context)

def BuildLibraryList(library_list, header):
    library_lists = []
    for library in library_list:
        properties = {}
        for head in header:
                properties[head[1]] = library[head[1]]
        library_lists.append(properties)
    return library_lists
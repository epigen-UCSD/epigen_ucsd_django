from django.shortcuts import render
from masterseq_app.models import LibraryInfo
# Create your views here.

'''
To add a column to scIndex or AllScLibs of libraryModel info, simply add the title of the coloumn wanted and the field name into a tuple
in header
list, eg ('Title of coloum', 'field_name')
'''
def scIndex(request):    
    #library_list = LibraryInfo.objects.filter(experiment_type='10xATAC').order_by('-date_started')
    library_list = LibraryInfo.objects.values().filter(experiment_type='10xATAC',team_member_initails=request.user).order_by('-date_started')
    header = [
        ('Library ID', 'library_id'),
        ('Library Description', 'library_description') ,
        ('Sample Info', 'sampleinfo_id'),
        ('Experiment Type','experiment_type'),
        ('Date Started' ,'date_started'),
        ('Date Completed' ,'date_completed')
    ]

    library_lists = []
    for library in library_list:
        properties = {}
        i = 0
        for head in header:
            properties[head[1]] = library[head[1]]
        library_lists.append(properties)
    print(library_lists)
    context = {
        'type' : 'All Single Cell Libraries',
        'header' : header,
        'library_lists': library_lists,
    }
    return render(request, 'singlecell_app/scIndex.html', context)

def AllScLibs(request):
    #library_list = LibraryInfo.objects.filter(experiment_type='10xATAC').order_by('-date_started')
    library_list = LibraryInfo.objects.values().filter(experiment_type='10xATAC').order_by('-date_started')
    header = [
        ('Library ID', 'library_id'),
        ('Library Description', 'library_description') ,
        ('Sample Info', 'sampleinfo_id'),
        ('Experiment Type','experiment_type'),
        ('Date Started' ,'date_started'),
        ('Date Completed' ,'date_completed')
    ]
    library_lists = []
    for library in library_list:
        properties = {}
        i = 0
        for head in header:
            properties[head[1]] = library[head[1]]
        library_lists.append(properties)
    print(library_lists)
    context = {
        'type' : 'All Single Cell Libraries',
        'header' : header,
        'library_lists': library_lists,
    }
    return render(request, 'singlecell_app/scIndex.html', context)
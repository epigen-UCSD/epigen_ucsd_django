from django.contrib.auth.decorators import login_required, permission_required
from .models import LibrariesSetQC,LibraryInSet
from masterseq_app.models import SequencingInfo
from django.db import transaction
from .forms import LibrariesSetQCCreationForm, LibrariesToIncludeCreatForm,ChIPLibrariesToIncludeCreatForm
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import JsonResponse
from itertools import groupby
from operator import itemgetter
from django.forms import formset_factory
from django.forms.models import model_to_dict
from django.conf import settings
import os
import subprocess

# Create your views here.
DisplayField1 = ['set_id','set_name','date_requested','experiment_type','url']
DisplayField2 = ['set_id','set_name','date_requested','requestor','experiment_type','url']
DisplayFieldforcollab = ['set_name','date_requested','experiment_type','genome','url']

def groupnumber(datalist):
    ranges =[]
    for k,g in groupby(enumerate(datalist),lambda x:x[0]-x[1]):
        group = (map(itemgetter(1),g))
        group = list(map(int,group))
        ranges.append((group[0],group[-1]))
    return ranges

def grouplibraries(librarieslist):
    groupedlibraries = []
    presuffix_number = {}
    for item in librarieslist:
        splititem = item.split('_',2)
        if len(splititem) == 1:
            groupedlibraries.append(item)
        else:
            prefix = item.split('_',2)[0]
            try:
                suffix = item.split('_',2)[2]
            except IndexError as e:
                suffix = ''
            presuffix = ':'.join([prefix,suffix])
            if presuffix not in presuffix_number.keys():
                presuffix_number[presuffix]=[]
            presuffix_number[presuffix].append(int(item.split('_',2)[1]))

    for k,v in presuffix_number.items():
        prefix = k.split(':')[0]
        suffix = k.split(':')[1]
        ranges = groupnumber(sorted(v))
        if not suffix:
            for x in ranges:
                if x[0] == x[1]:
                    groupedlibraries.append('_'.join([prefix,str(x[0])]))
                else:
                    start = '_'.join([prefix,str(x[0])])
                    end = '_'.join([prefix,str(x[1])])
                    groupedlibraries.append('-'.join([start,end]))
        else:
            for x in ranges:
                if x[0] == x[1]:
                    groupedlibraries.append('_'.join([prefix,str(x[0]),suffix]))
                else:
                    start = '_'.join([prefix,str(x[0]),suffix])
                    end = '_'.join([prefix,str(x[1]),suffix])
                    groupedlibraries.append('-'.join([start,end]))
    return ','.join(groupedlibraries)

def AllSetQCView(request):

    context = {
        'Sets_list': LibrariesSetQC.objects.all(),
        'DisplayField':DisplayField2,
    }
    return render(request, 'setqc_app/setqcinfo.html', context)

def UserSetQCView(request):
    SetQC_list = LibrariesSetQC.objects.filter(requestor=request.user)
    context = {
        'Sets_list': SetQC_list,
        'DisplayField':DisplayField1,
    }
    return render(request, 'setqc_app/usersetqcinfo.html', context)

@transaction.atomic
def SetQCCreateView(request):
    set_form = LibrariesSetQCCreationForm(request.POST or None)
    libraries_form = LibrariesToIncludeCreatForm(request.POST or None)
    ChIPLibrariesFormSet = formset_factory(ChIPLibrariesToIncludeCreatForm,can_delete=True)
    chiplibraries_formset = ChIPLibrariesFormSet(request.POST or None)
    if set_form.is_valid():
        setinfo = set_form.save(commit=False)
        setinfo.requestor = request.user
        set_ids = list(LibrariesSetQC.objects.values_list('set_id', flat=True))
        if not set_ids:
            setinfo.set_id = 'Set_165'
        else:
            maxid = max([int(x.split('_')[1]) for x in set_ids])
            setinfo.set_id = '_'.join(['Set',str(maxid+1)])
        if set_form.cleaned_data['experiment_type'] != 'ChIP-seq':
            if libraries_form.is_valid():
                setinfo.save()
                tosave_list = []
                librariestoinclude = libraries_form.cleaned_data['librariestoinclude']
                print(librariestoinclude)

                for item in librariestoinclude:
                    if item:
                        tosave_item = LibraryInSet(
                            librariesetqc=setinfo,
                            sequencinginfo=SequencingInfo.objects.get(sequencing_id=item),
                            )
                        tosave_list.append(tosave_item)
                LibraryInSet.objects.bulk_create(tosave_list)
                return redirect('setqc_app:setqc_detail',setqc_pk=setinfo.id)
        else:

            if chiplibraries_formset.is_valid():
                setinfo.save()
                groupnum = 1 
                tosave_list=[]
                for form in chiplibraries_formset.forms:
                    if form not in chiplibraries_formset.deleted_forms and form.cleaned_data:                       
                        libinputs = form.cleaned_data['librariestoincludeInput']
                        libips = form.cleaned_data['librariestoincludeIP']
                        for item in libinputs:
                            if item:
                                tosave_item = LibraryInSet(
                                    librariesetqc=setinfo,
                                    sequencinginfo=SequencingInfo.objects.get(sequencing_id=item),
                                    is_input=True,
                                    group_number=groupnum,
                                    )
                                tosave_list.append(tosave_item)
                        for item in libips:
                            if item:
                                tosave_item = LibraryInSet(
                                    librariesetqc=setinfo,
                                    sequencinginfo=SequencingInfo.objects.get(sequencing_id=item),
                                    is_input=False,
                                    group_number=groupnum,
                                    )
                                tosave_list.append(tosave_item)
                        groupnum += 1
                LibraryInSet.objects.bulk_create(tosave_list)
                return redirect('setqc_app:setqc_detail',setqc_pk=setinfo.id)

    context = {
        'set_form': set_form,
        'libraries_form': libraries_form,
        'sample_formset':chiplibraries_formset,
    }

    return render(request, 'setqc_app/setqcadd.html', context)


def SetQCDeleteView(request, setqc_pk):
    deleteset = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if deleteset.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    deleteset.delete()
    return redirect('setqc_app:usersetqcs')

@transaction.atomic
def SetQCUpdateView(request,setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    set_form = LibrariesSetQCCreationForm(request.POST or None, instance=setinfo)
    if setinfo.experiment_type != 'ChIP-seq':
        regset = LibraryInSet.objects.filter(librariesetqc=setinfo)
        librarieslist = [x.sequencinginfo.sequencing_id for x in regset]
        libraries_form = LibrariesToIncludeCreatForm(request.POST or None, \
            initial={'librariestoinclude': grouplibraries(librarieslist)})
        if set_form.is_valid() and libraries_form.is_valid():
            setinfo = set_form.save(commit=False)
            setinfo.save()
            tosave_list = []
            librariestoinclude = libraries_form.cleaned_data['librariestoinclude']
            print(librariestoinclude)
            setinfo.libraries_to_include.clear()
    
            for item in librariestoinclude:
                if item:
                    tosave_item = LibraryInSet(
                        librariesetqc=setinfo,
                        sequencinginfo=SequencingInfo.objects.get(sequencing_id=item),
                        )
                    tosave_list.append(tosave_item)
            LibraryInSet.objects.bulk_create(tosave_list)
            
    
            return redirect('setqc_app:setqc_detail',setqc_pk=setinfo.id)
        context = {
            'set_form': set_form,
            'libraries_form': libraries_form,
            'setinfo': setinfo,
        }
    
        return render(request, 'setqc_app/setqcupdate.html', context)
    else:
        chipset = LibraryInSet.objects.filter(librariesetqc=setinfo)
        groupitem = list(chipset.values_list('group_number', flat=True).distinct())
        initialgroup=[]
        for i in groupitem:
            temdic = {}
            temdic['librariestoincludeInput']=grouplibraries([x.sequencinginfo.sequencing_id for x in chipset.filter(group_number=i,is_input=True)])
            temdic['librariestoincludeIP']=grouplibraries([x.sequencinginfo.sequencing_id for x in chipset.filter(group_number=i,is_input=False)])
            initialgroup.append(temdic)
            print([x for x in chipset.filter(group_number=i,is_input=True)])
        ChIPLibrariesFormSet = formset_factory(ChIPLibrariesToIncludeCreatForm,can_delete=True)
        chiplibraries_formset = ChIPLibrariesFormSet(request.POST or None,
            initial=initialgroup)

        if set_form.is_valid() and chiplibraries_formset.is_valid():
            setinfo = set_form.save(commit=False)
            setinfo.save()
            groupnum = 1 
            tosave_list=[]
            for form in chiplibraries_formset.forms:
                if form not in chiplibraries_formset.deleted_forms and form.cleaned_data:
                    libinputs = form.cleaned_data['librariestoincludeInput']
                    libips = form.cleaned_data['librariestoincludeIP']
                    #print(libinputs)
                    #print(libips)
                    for item in libinputs:
                        if item:
                            tosave_item = LibraryInSet(
                                librariesetqc=setinfo,
                                sequencinginfo=SequencingInfo.objects.get(sequencing_id=item),
                                is_input=True,
                                group_number=groupnum,
                                )
                            tosave_list.append(tosave_item)
                    for item in libips:
                        if item:
                            tosave_item = LibraryInSet(
                                librariesetqc=setinfo,
                                sequencinginfo=SequencingInfo.objects.get(sequencing_id=item),
                                is_input=False,
                                group_number=groupnum,
                                )
                            tosave_list.append(tosave_item)
                    groupnum += 1
            setinfo.libraries_to_include.clear()
            print(tosave_list)
            LibraryInSet.objects.bulk_create(tosave_list)
            return redirect('setqc_app:setqc_detail',setqc_pk=setinfo.id)
        context = {
            'set_form': set_form,
            'sample_formset':chiplibraries_formset,
            'setinfo': setinfo,
        }
    
        return render(request, 'setqc_app/setqcchipupdate.html', context)


def GetNotesView(request,setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    # if setinfo.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
    #     raise PermissionDenied
    data = {}
    data['notes'] = setinfo.notes
    return JsonResponse(data)


@transaction.atomic
def RunSetQC(request, setqc_pk):
    libdir = settings.LIBQC_DIR
    setqcoutdir = settings.SETQC_DIR
    data = {}
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    allfolder = [ fname for fname in os.listdir(libdir) if os.path.isdir(os.path.join(libdir, fname))]
    librariesset = LibraryInSet.objects.filter(librariesetqc=setinfo)
    list1tem = list(librariesset.values_list('sequencinginfo', flat=True))
    list1 = [SequencingInfo.objects.values_list('sequencing_id', flat=True).get(id=x)
     for x in list1tem]

    if setinfo.experiment_type == 'ChIP-seq':

        list2 = list(librariesset.values_list('group_number', flat=True))
        list3 = list(librariesset.values_list('is_input', flat=True))
        writecontent = '\n'.join(['\t'.join(map(str,x)) for x in zip(list1,list2,list3)])
    else:
        # regset = setinfo.libraries_to_include.all()
        # list1 = [x.sequencing_id for x in regset]
        writecontent = '\n'.join(list1)

    #list1 is a list of libraries name in a specific set
    #check if the library folder exists and if it is finished
    for item in list1:
        if item not in allfolder:
            data['libdirnotexisterror'] = 'There is not a folder named ' + item
            return JsonResponse(data)
        else:
            if not os.path.isfile(os.path.join(libdir, item,'finished.txt')):
                data['notfinishederror'] = item +' is not finished'
                return JsonResponse(data)

    #write Set_**.txt to setqcoutdir
    try:
        with open(os.path.join(setqcoutdir,setinfo.set_id+'.txt'), 'w') as f:
            f.write(writecontent)
    except Exception as e:
        data['writeseterror'] = 'Unexpected writing to Set.txt Error!'
    setinfo.status='JobSubmitted'
    setinfo.save()

    #run setQC script
    cmd1 = './scripts/runsetqctest.sh ' + setinfo.set_id
    print(cmd1)
    p = subprocess.Popen(
        cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data['writesetdone'] = 1
    return JsonResponse(data)

def SetQCDetailView(request,setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    summaryfield = ['status','set_id','set_name','genome','collaborator','date_requested','requestor','experiment_type','notes','url','version']
    groupinputinfo = ''
    librariesset = LibraryInSet.objects.filter(librariesetqc=setinfo)
    list1tem = list(librariesset.values_list('sequencinginfo', flat=True))
    list1 = [SequencingInfo.objects.values_list('sequencing_id', flat=True).get(id=x)
     for x in list1tem]
    if setinfo.experiment_type == 'ChIP-seq':
        list2 = list(librariesset.values_list('group_number', flat=True))
        list3 = list(librariesset.values_list('is_input', flat=True))
        groupinputinfo = list(zip(list1,list2,list3))
    context = {
        'setinfo':setinfo,
        'summaryfield':summaryfield,
        'libraryinfo': list1,
        'groupinputinfo':groupinputinfo,
    }
    return render(request, 'setqc_app/details.html', context=context)


def CollaboratorSetQCView(request):
    SetQC_list = LibrariesSetQC.objects.filter(collaborator=request.user)
    context = {
        'Sets_list': SetQC_list,
        'DisplayField':DisplayFieldforcollab,
    }
    return render(request, 'setqc_app/collaboratorsetqcinfo.html', context)



def CollaboratorGetNotesView(request,setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.collaborator != request.user:
        raise PermissionDenied
    data = {}
    data['notes'] = setinfo.notes
    return JsonResponse(data)

def CollaboratorSetQCDetailView(request,setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.collaborator != request.user:
        raise PermissionDenied
    summaryfield = ['set_name','collaborator','date_requested','requestor','experiment_type','notes','url','version']
    groupinputinfo = ''
    librariesset = LibraryInSet.objects.filter(librariesetqc=setinfo)
    list1tem = list(librariesset.values_list('sequencinginfo', flat=True))
    list1 = [SequencingInfo.objects.values_list('sequencing_id', flat=True).get(id=x)
     for x in list1tem]
    if setinfo.experiment_type == 'ChIP-seq':
        list2 = list(librariesset.values_list('group_number', flat=True))
        list3 = list(librariesset.values_list('is_input', flat=True))
        groupinputinfo = list(zip(list1,list2,list3))
    context = {
        'setinfo':setinfo,
        'summaryfield':summaryfield,
        'libraryinfo': list1,
        'groupinputinfo':groupinputinfo,
    }
    return render(request, 'setqc_app/collaboratordetails.html', context=context)


















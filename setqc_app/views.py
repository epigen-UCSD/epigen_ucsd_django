from django.contrib.auth.decorators import login_required, permission_required
from .models import LibrariesSetQC,ChipLibraryInSet
from masterseq_app.models import SequencingInfo
from django.db import transaction
from .forms import LibrariesSetQCCreationForm, LibrariesToIncludeCreatForm,ChIPLibrariesToIncludeCreatForm
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from itertools import groupby
from operator import itemgetter
from django.forms import formset_factory
from django.forms.models import model_to_dict

# Create your views here.
DisplayField1 = ['setID','set_name','date_requested','experiment_type','url']
DisplayField2 = ['setID','set_name','date_requested','requestor','experiment_type','url']

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

@login_required
def AllSetQCView(request):

    context = {
        'Sets_list': LibrariesSetQC.objects.all(),
        'DisplayField':DisplayField2,
    }
    return render(request, 'setqc_app/setqcinfo.html', context)

@login_required
def UserSetQCView(request):
    SetQC_list = LibrariesSetQC.objects.filter(requestor=request.user)
    context = {
        'Sets_list': SetQC_list,
        'DisplayField':DisplayField1,
    }
    return render(request, 'setqc_app/usersetqcinfo.html', context)

@login_required
@transaction.atomic
def SetQCCreateView(request):
    set_form = LibrariesSetQCCreationForm(request.POST or None)
    libraries_form = LibrariesToIncludeCreatForm(request.POST or None)
    ChIPLibrariesFormSet = formset_factory(ChIPLibrariesToIncludeCreatForm,can_delete=True)
    chiplibraries_formset = ChIPLibrariesFormSet(request.POST or None)
    if set_form.is_valid():
        setinfo = set_form.save(commit=False)
        setinfo.requestor = request.user
        setids = list(LibrariesSetQC.objects.values_list('setID', flat=True))
        if not setids:
            setinfo.setID = 'Set_165'
        else:
            maxid = max([int(x.split('_')[1]) for x in setids])
            setinfo.setID = '_'.join(['Set',str(maxid+1)])
        if set_form.cleaned_data['experiment_type'] != 'ChIP-seq':
            if libraries_form.is_valid():
                setinfo.save()
                librariestoinclude = libraries_form.cleaned_data['librariestoinclude']
                print(librariestoinclude)

                for item in librariestoinclude:
                    if item:
                        setinfo.libraries_to_include.add(SequencingInfo.objects.get(sequencing_id=item))
        

                return redirect('setqc_app:usersetqcs')
        else:
            #if chiplibraries_formset.is_valid():
            print(chiplibraries_formset.empty_form)

            if chiplibraries_formset.is_valid():
                setinfo.save()
                groupnum = 1 
                tosave_list=[]
                for form in chiplibraries_formset.forms:
                    if form not in chiplibraries_formset.deleted_forms and form != chiplibraries_formset.empty_form:
                        libinputs = form.cleaned_data['librariestoincludeInput']
                        libips = form.cleaned_data['librariestoincludeIP']
                        for item in libinputs:
                            toave_item = ChipLibraryInSet(
                                librariesetqc=setinfo,
                                sequencinginfo=SequencingInfo.objects.get(sequencing_id=item),
                                is_input=True,
                                group_number=groupnum,
                                )
                            tosave_list.append(toave_item)
                        for item in libips:
                            toave_item = ChipLibraryInSet(
                                librariesetqc=setinfo,
                                sequencinginfo=SequencingInfo.objects.get(sequencing_id=item),
                                is_input=False,
                                group_number=groupnum,
                                )
                            tosave_list.append(toave_item)
                        groupnum += 1
                ChipLibraryInSet.objects.bulk_create(tosave_list)
                return redirect('setqc_app:usersetqcs')

    context = {
        'set_form': set_form,
        'libraries_form': libraries_form,
        'sample_formset':chiplibraries_formset,
    }

    return render(request, 'setqc_app/setqcadd.html', context)


@login_required
def SetQCDeleteView(request, setqc_pk):
    deleteset = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if deleteset.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    deleteset.delete()
    return redirect('setqc_app:usersetqcs')

@login_required
@transaction.atomic
def SetQCUpdateView(request,setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    set_form = LibrariesSetQCCreationForm(request.POST or None, instance=setinfo)
    if setinfo.experiment_type != 'ChIP-seq':
        librariesall = setinfo.libraries_to_include.all()
        librarieslist = list(librariesall.values_list('sequencing_id', flat=True))
        libraries_form = LibrariesToIncludeCreatForm(request.POST or None, \
            initial={'librariestoinclude': grouplibraries(librarieslist)})
        if set_form.is_valid() and libraries_form.is_valid():
            setinfo = set_form.save(commit=False)
            setinfo.save()
            librariestoinclude = libraries_form.cleaned_data['librariestoinclude']
            print(librariestoinclude)
            setinfo.libraries_to_include.clear()
    
            for item in librariestoinclude:
                if item:
                    setinfo.libraries_to_include.add(SequencingInfo.objects.get(sequencing_id=item))
            
    
            return redirect('setqc_app:usersetqcs')
        context = {
            'set_form': set_form,
            'libraries_form': libraries_form,
            'setinfo': setinfo,
        }
    
        return render(request, 'setqc_app/setqcupdate.html', context)
    else:
        #librariesall = setinfo.libraries_to_include_forChIP.all()
        chipset = ChipLibraryInSet.objects.filter(librariesetqc=setinfo)
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
                if form not in chiplibraries_formset.deleted_forms and form != chiplibraries_formset.empty_form:
                    libinputs = form.cleaned_data['librariestoincludeInput']
                    libips = form.cleaned_data['librariestoincludeIP']
                    #print(libinputs)
                    #print(libips)
                    for item in libinputs:
                        toave_item = ChipLibraryInSet(
                            librariesetqc=setinfo,
                            sequencinginfo=SequencingInfo.objects.get(sequencing_id=item),
                            is_input=True,
                            group_number=groupnum,
                            )
                        tosave_list.append(toave_item)
                    for item in libips:
                        toave_item = ChipLibraryInSet(
                            librariesetqc=setinfo,
                            sequencinginfo=SequencingInfo.objects.get(sequencing_id=item),
                            is_input=False,
                            group_number=groupnum,
                            )
                        tosave_list.append(toave_item)
                    groupnum += 1
            setinfo.libraries_to_include_forChIP.clear()
            ChipLibraryInSet.objects.bulk_create(tosave_list)
            return redirect('setqc_app:usersetqcs')
        context = {
            'set_form': set_form,
            'sample_formset':chiplibraries_formset,
            'setinfo': setinfo,
        }
    
        return render(request, 'setqc_app/setqcchipupdate.html', context)

@login_required
def GetNotesView(request,setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    data = {}
    data['notes'] = setinfo.notes
    return JsonResponse(data)






















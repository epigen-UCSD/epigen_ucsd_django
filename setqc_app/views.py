from django.contrib.auth.decorators import login_required, permission_required
from .models import LibrariesSetQC,LibraryInSet
from masterseq_app.models import SeqInfo,GenomeInfo
from django.db import transaction
from .forms import LibrariesSetQCCreationForm, LibrariesToIncludeCreatForm,\
ChIPLibrariesToIncludeCreatForm,SeqLabelGenomeCreationForm,BaseSeqLabelGenomeCreationFormSet
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
DisplayFieldforcollab = ['set_name','date_requested','experiment_type','url']
defaultgenome = {'human':'hg38','mouse':'mm10','rat':'rn6'}

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
                #print(librariestoinclude)

                for item in librariestoinclude:
                    if item:
                        tosave_item = LibraryInSet(
                            librariesetqc=setinfo,
                            seqinfo=SeqInfo.objects.get(seq_id=item),
                            )
                        tosave_list.append(tosave_item)
                LibraryInSet.objects.bulk_create(tosave_list)
                #return redirect('setqc_app:setqc_detail',setqc_pk=setinfo.id)
                return redirect('setqc_app:libraylabelgenome_add',setqc_pk=setinfo.id)
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
                                    seqinfo=SeqInfo.objects.get(seq_id=item),
                                    is_input=True,
                                    group_number=groupnum,
                                    )
                                tosave_list.append(tosave_item)
                        for item in libips:
                            if item:
                                tosave_item = LibraryInSet(
                                    librariesetqc=setinfo,
                                    seqinfo=SeqInfo.objects.get(seq_id=item),
                                    is_input=False,
                                    group_number=groupnum,
                                    )
                                tosave_list.append(tosave_item)
                        groupnum += 1
                LibraryInSet.objects.bulk_create(tosave_list)
                #return redirect('setqc_app:setqc_detail',setqc_pk=setinfo.id)
                return redirect('setqc_app:libraylabelgenome_add',setqc_pk=setinfo.id)

    context = {
        'set_form': set_form,
        'libraries_form': libraries_form,
        'sample_formset':chiplibraries_formset,
    }

    return render(request, 'setqc_app/setqcadd.html', context)

@transaction.atomic
def SetQCgenomelabelCreateView(request,setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    regset = LibraryInSet.objects.filter(librariesetqc=setinfo).order_by('seqinfo')
    temdic = {}
    formsetcustom = []
    initaldic = []
    speci_list = []
    for x in regset:
        temdic = {}
        temdic['sequencingid'] = x.seqinfo.seq_id
        speci = x.seqinfo.libraryinfo.sampleinfo.species
        speci_list.append(speci)
        temdic['speciesbelong'] = speci
        temdic['genomeinthisset'] = defaultgenome[speci]
        # if LibraryInSet.objects.filter(seqinfo=x.seqinfo).count()>1:
        #     obj = LibraryInSet.objects.filter(seqinfo=x.seqinfo).order_by('-pk')[1]
        #     if obj.label:
        #         temdic['lableinthisset'] = obj.label
        #     else:
        #         temdic['lableinthisset'] = x.seqinfo.seq_id
        # else:
        #     temdic['lableinthisset'] = x.seqinfo.seq_id

        if x.seqinfo.default_label:
            temdic['lableinthisset'] = x.seqinfo.default_label
        else:
            temdic['lableinthisset'] = x.seqinfo.seq_id
        initaldic.append(temdic)
    librarieslabelgenomeFormSet = formset_factory(SeqLabelGenomeCreationForm,
        can_delete=False,
        formset=BaseSeqLabelGenomeCreationFormSet,
        extra=0)
    formsetcustom = librarieslabelgenomeFormSet(request.POST or None,
        initial=initaldic,
        form_kwargs={'thisspecies_list': speci_list}
        )
    if formsetcustom.is_valid():
        #print('right')
        for form in formsetcustom.forms:
            #print(form)
            seqidtm = form.cleaned_data['sequencingid']
            genometm = form.cleaned_data['genomeinthisset']
            labeltm = form.cleaned_data['lableinthisset']
            obj = regset.get(seqinfo=SeqInfo.objects.get(seq_id=seqidtm))
            obj.genome = GenomeInfo.objects.get(genome_name=genometm)
            obj.label = labeltm
            obj.save()
        return redirect('setqc_app:setqc_detail',setqc_pk=setinfo.id)

    context = {
        'formsetcustom': formsetcustom,
    }

    return render(request, 'setqc_app/librarylabelgenomeadd.html', context)


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
    essentialfields = ['set_name','experiment_type']
    flag = 0
    if setinfo.experiment_type != 'ChIP-seq':
        regset = LibraryInSet.objects.filter(librariesetqc=setinfo)
        librarieslist = [x.seqinfo.seq_id for x in regset]
        libraries_form = LibrariesToIncludeCreatForm(request.POST or None, \
            initial={'librariestoinclude': grouplibraries(librarieslist)})
        if set_form.is_valid() and libraries_form.is_valid():
            setinfo = set_form.save(commit=False)
            setinfo.save()           
            for x in essentialfields:
                if x in set_form.changed_data:
                    flag = 1
                    break

            if libraries_form.has_changed():
                flag = 1
                tosave_list = []
                librariestoinclude = libraries_form.cleaned_data['librariestoinclude']
                #print(librariestoinclude)
                setinfo.libraries_to_include.clear()
        
                for item in librariestoinclude:
                    if item:
                        tosave_item = LibraryInSet(
                            librariesetqc=setinfo,
                            seqinfo=SeqInfo.objects.get(seq_id=item),
                            )
                        tosave_list.append(tosave_item)
                LibraryInSet.objects.bulk_create(tosave_list)

            if flag == 1:
                setinfo.url = ''
                setinfo.version = ''
                setinfo.status = 'ClickToSubmit'
                setinfo.save()
 
            return redirect('setqc_app:libraylabelgenome_update',setqc_pk=setinfo.id)
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
            temdic['librariestoincludeInput']=grouplibraries([x.seqinfo.seq_id for x in chipset.filter(group_number=i,is_input=True)])
            temdic['librariestoincludeIP']=grouplibraries([x.seqinfo.seq_id for x in chipset.filter(group_number=i,is_input=False)])
            initialgroup.append(temdic)
            #print([x for x in chipset.filter(group_number=i,is_input=True)])
        ChIPLibrariesFormSet = formset_factory(ChIPLibrariesToIncludeCreatForm,can_delete=True)
        chiplibraries_formset = ChIPLibrariesFormSet(request.POST or None,
            initial=initialgroup)

        if set_form.is_valid() and chiplibraries_formset.is_valid():
            setinfo = set_form.save(commit=False)
            setinfo.save()
            for x in essentialfields:
                if x in set_form.changed_data:
                    flag = 1
                    break
                                 
            if chiplibraries_formset.has_changed():
                flag = 1
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
                                    seqinfo=SeqInfo.objects.get(seq_id=item),
                                    is_input=True,
                                    group_number=groupnum,
                                    )
                                tosave_list.append(tosave_item)
                        for item in libips:
                            if item:
                                tosave_item = LibraryInSet(
                                    librariesetqc=setinfo,
                                    seqinfo=SeqInfo.objects.get(seq_id=item),
                                    is_input=False,
                                    group_number=groupnum,
                                    )
                                tosave_list.append(tosave_item)
                        groupnum += 1
                setinfo.libraries_to_include.clear()
                #print(tosave_list)
                LibraryInSet.objects.bulk_create(tosave_list)
            if flag == 1:
                setinfo.url = ''
                setinfo.version = ''
                setinfo.status = 'ClickToSubmit'
                setinfo.save()            
            return redirect('setqc_app:libraylabelgenome_update',setqc_pk=setinfo.id)
        context = {
            'set_form': set_form,
            'sample_formset':chiplibraries_formset,
            'setinfo': setinfo,
        }
    
        return render(request, 'setqc_app/setqcchipupdate.html', context)
@transaction.atomic
def SetQCgenomelabelUpdateView(request,setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    regset = LibraryInSet.objects.filter(librariesetqc=setinfo).order_by('seqinfo')
    temdic = {}
    formsetcustom = []
    initaldic = []
    speci_list = []
    for x in regset:
        temdic = {}
        temdic['sequencingid'] = x.seqinfo.seq_id
        speci = x.seqinfo.libraryinfo.sampleinfo.species
        speci_list.append(speci)
        temdic['speciesbelong'] = speci
        temdic['genomeinthisset'] = defaultgenome[speci]
        if x.label:
            temdic['lableinthisset'] = x.label
        else:
            if x.seqinfo.default_label:
                temdic['lableinthisset'] = x.seqinfo.default_label
            else:
                temdic['lableinthisset'] = x.seqinfo.seq_id

        initaldic.append(temdic)
    librarieslabelgenomeFormSet = formset_factory(SeqLabelGenomeCreationForm,
        can_delete=False,
        formset=BaseSeqLabelGenomeCreationFormSet,
        extra=0)
    formsetcustom = librarieslabelgenomeFormSet(request.POST or None,
        initial=initaldic,
        form_kwargs={'thisspecies_list': speci_list}
        )
    if formsetcustom.is_valid():
        #print('right')
        for form in formsetcustom.forms:
            #print(form)
            seqidtm = form.cleaned_data['sequencingid']
            genometm = form.cleaned_data['genomeinthisset']
            labeltm = form.cleaned_data['lableinthisset']
            obj = regset.get(seqinfo=SeqInfo.objects.get(seq_id=seqidtm))
            obj.genome = GenomeInfo.objects.get(genome_name=genometm)
            obj.label = labeltm
            obj.save()
        if formsetcustom.has_changed():
            setinfo.url = ''
            setinfo.version = ''
            setinfo.status = 'ClickToSubmit'
            setinfo.save()             
        return redirect('setqc_app:setqc_detail',setqc_pk=setinfo.id)

    context = {
        'formsetcustom': formsetcustom,
    }

    return render(request, 'setqc_app/librarylabelgenomeadd.html', context)

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
    list1tem = list(librariesset.values_list('seqinfo', flat=True))
    list1 = [SeqInfo.objects.values_list('seq_id', flat=True).get(id=x)
     for x in list1tem]
    list4 = [GenomeInfo.objects.values_list('genome_name', flat=True).get(id=x) for x in list(librariesset.values_list('genome', flat=True))]
    list5 = list(librariesset.values_list('label', flat=True))
    seqstatus = []
    for item in list1:
        if item not in allfolder:
            seqstatus.append('No')
        else:
            if not os.path.isfile(os.path.join(libdir, item,'finished.txt')):
                seqstatus.append('No')
            else:
                seqstatus.append('Yes')
    if setinfo.experiment_type == 'ChIP-seq':

        list2 = list(librariesset.values_list('group_number', flat=True))
        list3 = list(librariesset.values_list('is_input', flat=True))
        writecontent = '\n'.join(['\t'.join(map(str,x)) for x in zip(list1,list2,list3,list4,list5,seqstatus)])
        featureheader = ['Library ID','Group ID','Is Input','Genome','Label','Processed Or Not']
    else:
        # regset = setinfo.libraries_to_include.all()
        # list1 = [x.seq_id for x in regset]
        writecontent = '\n'.join(['\t'.join(map(str,x)) for x in zip(list1,list4,list5,seqstatus)])
        featureheader = ['Library ID','Genome','Label','Processed Or Not']
    # #list1 is a list of libraries name in a specific set
    # #check if the library folder exists and if it is finished
    # for item in list1:
    #     if item not in allfolder:
    #         data['libdirnotexisterror'] = 'There is not a folder named ' + item
    #         return JsonResponse(data)
    #     else:
    #         if not os.path.isfile(os.path.join(libdir, item,'finished.txt')):
    #             data['notfinishederror'] = item +' is not finished'
    #             return JsonResponse(data)

    #write Set_**.txt to setqcoutdir
    if os.path.isfile(os.path.join(setqcoutdir,setinfo.set_id+'.txt')):
        data['setidexisterror'] = setinfo.set_id+'.txt is already existed. Do you want to override it and continue to run the pipeline and SetQC script?'
        print(data['setidexisterror'])
        return JsonResponse(data)
    try:
        with open(os.path.join(setqcoutdir,setinfo.set_id+'.txt'), 'w') as f:
            f.write('\t'.join(featureheader)+'\n')
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
@transaction.atomic
def RunSetQC2(request, setqc_pk):
    libdir = settings.LIBQC_DIR
    setqcoutdir = settings.SETQC_DIR
    data = {}
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    allfolder = [ fname for fname in os.listdir(libdir) if os.path.isdir(os.path.join(libdir, fname))]
    librariesset = LibraryInSet.objects.filter(librariesetqc=setinfo)
    list1tem = list(librariesset.values_list('seqinfo', flat=True))
    list1 = [SeqInfo.objects.values_list('seq_id', flat=True).get(id=x)
     for x in list1tem]
    list4 = [GenomeInfo.objects.values_list('genome_name', flat=True).get(id=x) for x in list(librariesset.values_list('genome', flat=True))]
    list5 = list(librariesset.values_list('label', flat=True))
    seqstatus = []
    for item in list1:
        if item not in allfolder:
            seqstatus.append('No')
        else:
            if not os.path.isfile(os.path.join(libdir, item,'finished.txt')):
                seqstatus.append('No')
            else:
                seqstatus.append('Yes')
    if setinfo.experiment_type == 'ChIP-seq':

        list2 = list(librariesset.values_list('group_number', flat=True))
        list3 = list(librariesset.values_list('is_input', flat=True))
        writecontent = '\n'.join(['\t'.join(map(str,x)) for x in zip(list1,list2,list3,list4,list5,seqstatus)])
        featureheader = ['Library ID','Group ID','Is Input','Genome','Label','Processed Or Not']
    else:
        # regset = setinfo.libraries_to_include.all()
        # list1 = [x.seq_id for x in regset]
        writecontent = '\n'.join(['\t'.join(map(str,x)) for x in zip(list1,list4,list5,seqstatus)])
        featureheader = ['Library ID','Genome','Label','Processed Or Not']
    # #list1 is a list of libraries name in a specific set
    # #check if the library folder exists and if it is finished
    # for item in list1:
    #     if item not in allfolder:
    #         data['libdirnotexisterror'] = 'There is not a folder named ' + item
    #         return JsonResponse(data)
    #     else:
    #         if not os.path.isfile(os.path.join(libdir, item,'finished.txt')):
    #             data['notfinishederror'] = item +' is not finished'
    #             return JsonResponse(data)

    #write Set_**.txt to setqcoutdir
    try:
        with open(os.path.join(setqcoutdir,setinfo.set_id+'.txt'), 'w') as f:
            f.write('\t'.join(featureheader)+'\n')
            f.write(writecontent)
    except Exception as e:
        data['writeseterror'] = 'Unexpected writing to Set.txt Error!'
    setinfo.status='JobSubmitted'
    setinfo.save()

    #run setQC script
    cmd1 = './utility/runsetqctest.sh ' + setinfo.set_id
    print(cmd1)
    p = subprocess.Popen(
        cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data['writesetdone'] = 1
    return JsonResponse(data)


def SetQCDetailView(request,setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    libdir = settings.LIBQC_DIR
    allfolder = [ fname for fname in os.listdir(libdir) if os.path.isdir(os.path.join(libdir, fname))]
    summaryfield = ['status','set_id','set_name','collaborator','date_requested','requestor','experiment_type','notes','url','version']
    groupinputinfo = ''
    librariesset = LibraryInSet.objects.filter(librariesetqc=setinfo).order_by('group_number','-is_input')
    list1tem = list(librariesset.values_list('seqinfo', flat=True))
    list1 = [SeqInfo.objects.values_list('seq_id', flat=True).get(id=x) for x in list1tem]
    seqstatus = []
    list4 = [GenomeInfo.objects.values_list('genome_name', flat=True).get(id=x) for x in list(librariesset.values_list('genome', flat=True))]
    list5 = list(librariesset.values_list('label', flat=True))
    for item in list1:
        if item not in allfolder:
            seqstatus.append('No')
        else:
            if not os.path.isfile(os.path.join(libdir, item,'finished.txt')):
                seqstatus.append('No')
            else:
                seqstatus.append('Yes')

    if setinfo.experiment_type == 'ChIP-seq':
        list2 = list(librariesset.values_list('group_number', flat=True))
        list3 = list(librariesset.values_list('is_input', flat=True))
        featureinfo = list(zip(list1,list2,list3,list4,list5,seqstatus))
        featureheader = ['Library ID','Group ID','Is Input','Genome','Label','Processed']
    else:
        featureinfo = list(zip(list1,list4,list5,seqstatus))
        featureheader = ['Library ID','Genome','Label','Processed']
    context = {
        'setinfo':setinfo,
        'summaryfield':summaryfield,
        'featureinfo':featureinfo,
        'featureheader':featureheader
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
    list1tem = list(librariesset.values_list('seqinfo', flat=True))
    list1 = [SeqInfo.objects.values_list('seq_id', flat=True).get(id=x)
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


















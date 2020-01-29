from django.contrib.auth.decorators import login_required, permission_required
from .models import LibrariesSetQC, LibraryInSet
from masterseq_app.models import SeqInfo, GenomeInfo, SampleInfo, LibraryInfo
from django.db import transaction
from .forms import LibrariesSetQCCreationForm, LibrariesToIncludeCreatForm,\
    ChIPLibrariesToIncludeCreatForm, SeqLabelGenomeCreationForm, BaseSeqLabelGenomeCreationFormSet,EncodeSetForm
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
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.http import HttpResponse
import re

# Create your views here.
DisplayField1 = ['set_id', 'set_name',
                 'last_modified', 'experiment_type', 'url', 'version']
DisplayField2 = ['set_id', 'set_name', 'last_modified',
                 'requestor', 'experiment_type', '#libraries','url', 'version']
defaultgenome = {'human': 'hg38', 'mouse': 'mm10',
                 'rat': 'rn6', 'cattle': 'ARS-UCD1.2',
                 'green monkey':'chlSab2', 'pig-tailed macaque':'Mnem1.0',
                 'fruit fly':'dm6'}


def groupnumber(datalist):
    ranges = []
    for k, g in groupby(enumerate(datalist), lambda x: x[0]-x[1]):
        group = (map(itemgetter(1), g))
        group = list(map(int, group))
        ranges.append((group[0], group[-1]))
    return ranges


def grouplibraries(librarieslist):
    groupedlibraries = []
    presuffix_number = {}
    for item in librarieslist:
        splititem = item.split('_', 2)
        if len(splititem) == 1:
            groupedlibraries.append(item)
        else:
            prefix = item.split('_', 2)[0]
            try:
                suffix = item.split('_', 2)[2]
            except IndexError as e:
                suffix = ''
            presuffix = ':'.join([prefix, suffix])
            if presuffix not in presuffix_number.keys():
                presuffix_number[presuffix] = []
            presuffix_number[presuffix].append(int(item.split('_', 2)[1]))

    for k, v in presuffix_number.items():
        prefix = k.split(':')[0]
        suffix = k.split(':')[1]
        ranges = groupnumber(sorted(v))
        if not suffix:
            for x in ranges:
                if x[0] == x[1]:
                    groupedlibraries.append('_'.join([prefix, str(x[0])]))
                else:
                    start = '_'.join([prefix, str(x[0])])
                    end = '_'.join([prefix, str(x[1])])
                    groupedlibraries.append('-'.join([start, end]))
        else:
            for x in ranges:
                if x[0] == x[1]:
                    groupedlibraries.append(
                        '_'.join([prefix, str(x[0]), suffix]))
                else:
                    start = '_'.join([prefix, str(x[0]), suffix])
                    end = '_'.join([prefix, str(x[1]), suffix])
                    groupedlibraries.append('-'.join([start, end]))
    return ','.join(groupedlibraries)


def grouplibrariesOrderKeeped(librarieslist):
    groupedlibraries = []
    presuffix_last = ''
    presuffix_number = {}
    for item in librarieslist:
        splititem = item.split('_', 2)
        if len(splititem) == 1:
            groupedlibraries.append(item)
        else:
            prefix = item.split('_', 2)[0]
            try:
                suffix = item.split('_', 2)[2]
            except IndexError as e:
                suffix = ''
            presuffix = ':'.join([prefix, suffix])
            if presuffix == presuffix_last:
                presuffix_number.append(int(item.split('_', 2)[1]))
            else:
                if presuffix_last:
                    prefix = presuffix_last.split(':')[0]
                    suffix = presuffix_last.split(':')[1]
                    ranges = groupnumber(presuffix_number)
                    if not suffix:
                        for x in ranges:
                            if x[0] == x[1]:
                                groupedlibraries.append(
                                    '_'.join([prefix, str(x[0])]))
                            else:
                                start = '_'.join([prefix, str(x[0])])
                                end = '_'.join([prefix, str(x[1])])
                                groupedlibraries.append('-'.join([start, end]))
                    else:
                        for x in ranges:
                            if x[0] == x[1]:
                                groupedlibraries.append(
                                    '_'.join([prefix, str(x[0]), suffix]))
                            else:
                                start = '_'.join([prefix, str(x[0]), suffix])
                                end = '_'.join([prefix, str(x[1]), suffix])
                                groupedlibraries.append('-'.join([start, end]))
                presuffix_last = presuffix
                presuffix_number = []
                presuffix_number.append(int(item.split('_', 2)[1]))
    if presuffix_last:
        prefix = presuffix_last.split(':')[0]
        suffix = presuffix_last.split(':')[1]
        ranges = groupnumber(presuffix_number)
        if not suffix:
            for x in ranges:
                if x[0] == x[1]:
                    groupedlibraries.append('_'.join([prefix, str(x[0])]))
                else:
                    start = '_'.join([prefix, str(x[0])])
                    end = '_'.join([prefix, str(x[1])])
                    groupedlibraries.append('-'.join([start, end]))
        else:
            for x in ranges:
                if x[0] == x[1]:
                    groupedlibraries.append(
                        '_'.join([prefix, str(x[0]), suffix]))
                else:
                    start = '_'.join([prefix, str(x[0]), suffix])
                    end = '_'.join([prefix, str(x[1]), suffix])
                    groupedlibraries.append('-'.join([start, end]))

    return ','.join(groupedlibraries)


def AllSetQCView(request):

    Sets_list = LibrariesSetQC.objects.all().select_related('requestor')
    context = {
        'Sets_list': Sets_list,
        'DisplayField': DisplayField2,
    }
    if not request.user.groups.filter(name='bioinformatics').exists():
        return render(request, 'setqc_app/setqcinfo.html', context)
    else:
        return render(request, 'setqc_app/setqcinfo_bio.html', context)


def UserSetQCView(request):
    SetQC_list = LibrariesSetQC.objects.filter(requestor=request.user)
    context = {
        'Sets_list': SetQC_list,
        'DisplayField': DisplayField1,
    }
    return render(request, 'setqc_app/usersetqcinfo.html', context)


@transaction.atomic
def SetQCCreateView(request):

    libraries_form = LibrariesToIncludeCreatForm(request.POST or None)
    ChIPLibrariesFormSet = formset_factory(
        ChIPLibrariesToIncludeCreatForm, can_delete=True)
    chiplibraries_formset = ChIPLibrariesFormSet(request.POST or None)
    if request.method == 'POST':
        post = request.POST.copy()
        if post['collaborator']:
            obj = get_object_or_404(
                User, id=post['collaborator'].split(':')[0])
            groupinfo = get_object_or_404(
                Group, name=post['collaborator'].strip(')').split('(')[-1])
            post['collaborator'] = obj.id
        else:
            groupinfo = None
        set_form = LibrariesSetQCCreationForm(post)
        if set_form.is_valid():
            setinfo = set_form.save(commit=False)
            setinfo.requestor = request.user
            setinfo.group = groupinfo
            set_ids = list(
                LibrariesSetQC.objects.values_list('set_id', flat=True))
            if not set_ids:
                setinfo.set_id = 'Set_165'
            else:
                maxid = max([int(x.split('_')[1]) for x in set_ids])
                setinfo.set_id = '_'.join(['Set', str(maxid+1)])
            if set_form.cleaned_data['experiment_type'] != 'ChIP-seq':
                if libraries_form.is_valid():
                    setinfo.save()
                    tosave_list = []
                    librariestoinclude = libraries_form.cleaned_data['librariestoinclude']
                    # print(librariestoinclude)

                    for item in librariestoinclude:
                        if item:
                            tosave_item = LibraryInSet(
                                librariesetqc=setinfo,
                                seqinfo=SeqInfo.objects.get(seq_id=item),
                            )
                            tosave_list.append(tosave_item)

                    LibraryInSet.objects.bulk_create(tosave_list)
                    # return redirect('setqc_app:setqc_detail',setqc_pk=setinfo.id)
                    return redirect('setqc_app:libraylabelgenome_add', setqc_pk=setinfo.id)
            else:

                if chiplibraries_formset.is_valid():
                    setinfo.save()
                    groupnum = 1
                    tosave_list = []
                    for form in chiplibraries_formset.forms:
                        if form not in chiplibraries_formset.deleted_forms and form.cleaned_data:
                            libinputs = form.cleaned_data['librariestoincludeInput']
                            libips = form.cleaned_data['librariestoincludeIP']
                            for item in libinputs:
                                if item:
                                    tosave_item = LibraryInSet(
                                        librariesetqc=setinfo,
                                        seqinfo=SeqInfo.objects.get(
                                            seq_id=item),
                                        is_input=True,
                                        group_number=groupnum,
                                    )
                                    tosave_list.append(tosave_item)
                            for item in libips:
                                if item:
                                    tosave_item = LibraryInSet(
                                        librariesetqc=setinfo,
                                        seqinfo=SeqInfo.objects.get(
                                            seq_id=item),
                                        is_input=False,
                                        group_number=groupnum,
                                    )
                                    tosave_list.append(tosave_item)
                            groupnum += 1
                    LibraryInSet.objects.bulk_create(tosave_list)
                    # return redirect('setqc_app:setqc_detail',setqc_pk=setinfo.id)
                    return redirect('setqc_app:libraylabelgenome_add', setqc_pk=setinfo.id)
    else:
        set_form = LibrariesSetQCCreationForm(None)

    context = {
        'set_form': set_form,
        'libraries_form': libraries_form,
        'sample_formset': chiplibraries_formset,
    }

    return render(request, 'setqc_app/setqcadd.html', context)


@transaction.atomic
def SetQCgenomelabelCreateView(request, setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    regset = LibraryInSet.objects.filter(
        librariesetqc=setinfo).order_by('pk')
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
                                                form_kwargs={
                                                    'thisspecies_list': speci_list}
                                                )
    if formsetcustom.is_valid():
        # print('right')
        for form in formsetcustom.forms:
            # print(form)
            seqidtm = form.cleaned_data['sequencingid']
            genometm = form.cleaned_data['genomeinthisset']
            labeltm = form.cleaned_data['lableinthisset']
            obj = regset.get(seqinfo=SeqInfo.objects.get(seq_id=seqidtm))
            obj.genome = GenomeInfo.objects.get(genome_name=genometm)
            obj.label = labeltm
            obj.save()
        # return redirect('setqc_app:setqc_detail',setqc_pk=setinfo.id)
        return redirect('setqc_app:usersetqcs')

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
def SetQCUpdateView(request, setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    essentialfields = ['set_name', 'experiment_type']

    flag = 0
    if setinfo.experiment_type != 'ChIP-seq':
        regset = LibraryInSet.objects.filter(
            librariesetqc=setinfo).order_by('pk')
        librarieslist = [x.seqinfo.seq_id for x in regset]
        libraries_form = LibrariesToIncludeCreatForm(request.POST or None,
                                                     initial={'librariestoinclude': grouplibrariesOrderKeeped(librarieslist)})
        if request.method == 'POST':
            post = request.POST.copy()
            if post['collaborator']:
                obj = get_object_or_404(
                    User, id=post['collaborator'].split(':')[0])
                groupinfo = get_object_or_404(
                    Group, name=post['collaborator'].strip(')').split('(')[-1])
                post['collaborator'] = obj.id
            else:
                groupinfo = None
            set_form = LibrariesSetQCCreationForm(post, instance=setinfo)
            if set_form.is_valid() and libraries_form.is_valid():
                setinfo = set_form.save(commit=False)
                setinfo.group = groupinfo
                setinfo.save()
                for x in essentialfields:
                    if x in set_form.changed_data:
                        flag = 1
                        break

                if libraries_form.has_changed():
                    flag = 1
                    tosave_list = []
                    librariestoinclude = libraries_form.cleaned_data['librariestoinclude']
                    # print(librariestoinclude)
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

                return redirect('setqc_app:libraylabelgenome_update', setqc_pk=setinfo.id)
        else:
            set_form = LibrariesSetQCCreationForm(instance=setinfo)

        context = {
            'set_form': set_form,
            'libraries_form': libraries_form,
            'setinfo': setinfo,
        }

        return render(request, 'setqc_app/setqcupdate.html', context)
    else:
        chipset = LibraryInSet.objects.filter(librariesetqc=setinfo)
        groupitem = list(chipset.values_list(
            'group_number', flat=True).distinct())
        initialgroup = []
        for i in groupitem:
            temdic = {}
            temdic['librariestoincludeInput'] = grouplibrariesOrderKeeped(
                [x.seqinfo.seq_id for x in chipset.filter(group_number=i, is_input=True).order_by('pk')])
            temdic['librariestoincludeIP'] = grouplibrariesOrderKeeped(
                [x.seqinfo.seq_id for x in chipset.filter(group_number=i, is_input=False).order_by('pk')])
            initialgroup.append(temdic)
            #print([x for x in chipset.filter(group_number=i,is_input=True)])
        ChIPLibrariesFormSet = formset_factory(
            ChIPLibrariesToIncludeCreatForm, can_delete=True)
        chiplibraries_formset = ChIPLibrariesFormSet(request.POST or None,
                                                     initial=initialgroup)
        if request.method == 'POST':
            post = request.POST.copy()
            if post['collaborator']:
                obj = get_object_or_404(
                    User, id=post['collaborator'].split(':')[0])
                groupinfo = get_object_or_404(
                    Group, name=post['collaborator'].strip(')').split('(')[-1])
                post['collaborator'] = obj.id
            else:
                groupinfo = None
            set_form = LibrariesSetQCCreationForm(post, instance=setinfo)
            if set_form.is_valid() and chiplibraries_formset.is_valid():
                setinfo = set_form.save(commit=False)
                setinfo.group = groupinfo
                setinfo.save()
                for x in essentialfields:
                    if x in set_form.changed_data:
                        flag = 1
                        break

                if chiplibraries_formset.has_changed():
                    flag = 1
                    groupnum = 1
                    tosave_list = []
                    for form in chiplibraries_formset.forms:
                        if form not in chiplibraries_formset.deleted_forms and form.cleaned_data:
                            libinputs = form.cleaned_data['librariestoincludeInput']
                            libips = form.cleaned_data['librariestoincludeIP']
                            # print(libinputs)
                            # print(libips)
                            for item in libinputs:
                                if item:
                                    tosave_item = LibraryInSet(
                                        librariesetqc=setinfo,
                                        seqinfo=SeqInfo.objects.get(
                                            seq_id=item),
                                        is_input=True,
                                        group_number=groupnum,
                                    )
                                    tosave_list.append(tosave_item)
                            for item in libips:
                                if item:
                                    tosave_item = LibraryInSet(
                                        librariesetqc=setinfo,
                                        seqinfo=SeqInfo.objects.get(
                                            seq_id=item),
                                        is_input=False,
                                        group_number=groupnum,
                                    )
                                    tosave_list.append(tosave_item)
                            groupnum += 1
                    setinfo.libraries_to_include.clear()
                    # print(tosave_list)
                    LibraryInSet.objects.bulk_create(tosave_list)
                if flag == 1:
                    setinfo.url = ''
                    setinfo.version = ''
                    setinfo.status = 'ClickToSubmit'
                    setinfo.save()
                return redirect('setqc_app:libraylabelgenome_update', setqc_pk=setinfo.id)
        else:
            set_form = LibrariesSetQCCreationForm(instance=setinfo)

        context = {
            'set_form': set_form,
            'sample_formset': chiplibraries_formset,
            'setinfo': setinfo,
        }

        return render(request, 'setqc_app/setqcchipupdate.html', context)


@transaction.atomic
def SetQCgenomelabelUpdateView(request, setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    regset = LibraryInSet.objects.filter(
        librariesetqc=setinfo).order_by('pk')
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
                                                form_kwargs={
                                                    'thisspecies_list': speci_list}
                                                )
    if formsetcustom.is_valid():
        # print('right')
        for form in formsetcustom.forms:
            # print(form)
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
        # return redirect('setqc_app:setqc_detail',setqc_pk=setinfo.id)
        return redirect('setqc_app:usersetqcs')

    context = {
        'formsetcustom': formsetcustom,
    }

    return render(request, 'setqc_app/librarylabelgenomeadd.html', context)


def GetNotesView(request, setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    # if setinfo.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
    #     raise PermissionDenied
    data = {}
    data['notes'] = setinfo.notes
    return JsonResponse(data)


@transaction.atomic
def RunSetQC(request, setqc_pk):
    libdir = settings.LIBQC_DIR
    fastqdir = settings.FASTQ_DIR
    setqcoutdir = settings.SETQC_DIR
    tenxdir = settings.TENX_DIR
    data = {}
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied

    # Only add folders in libdir that are directories
    allfolder = [fname for fname in os.listdir(
        libdir) if os.path.isdir(os.path.join(libdir, fname))]

    outinfo = list(LibraryInSet.objects.filter(librariesetqc=setinfo).
                   select_related('seqinfo__libraryinfo__sampleinfo', 'seqinfo__machine', 'genome').
                   values('seqinfo__seq_id', 'group_number', 'is_input', 'genome__genome_name',
                          'label', 'seqinfo__read_type', 'seqinfo__libraryinfo__sampleinfo__sample_id',
                          'seqinfo__libraryinfo__sampleinfo__species', 'seqinfo__libraryinfo__experiment_type',
                          'seqinfo__machine__machine_name').order_by('pk'))

    list1 = [x['seqinfo__seq_id'] for x in outinfo]
    list_readtype = [x['seqinfo__read_type'] for x in outinfo]
    seqstatus = {}
    i = 0
    for item in list1:
        if item not in allfolder:
            seqstatus[item] = 'No'
        else:
            if not os.path.isfile(os.path.join(libdir, item, '.finished.txt')):
                seqstatus[item] = 'No'
            else:
                seqstatus[item] = 'Yes'

        reps = ['1']
        reps = reps + item.split('_')[2:]
        mainname = '_'.join(item.split('_')[0:2])
        if seqstatus[item] == 'No':
            if not item.startswith('ENCODE_'):
                if list_readtype[i] == 'PE':
                    r1 = item+'_R1.fastq.gz'
                    r2 = item+'_R2.fastq.gz'
                    if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                        for j in set(reps):
                            if j == '1':
                                repname = mainname
                            else:
                                repname = '_'.join([mainname, j])   

                            r1 = repname+'_R1.fastq.gz'
                            r2 = repname+'_R2.fastq.gz'
                            try:
                                if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                                    data['fastqerror'] = 'There is at least one library without fastq file. Please go to the setQC detail page.'
                                    return JsonResponse(data)
                            except Exception as e:
                                data['fastqerror'] = 'There is at least one library without fastq file ready. Please go to the setQC detail page.'
                                print(e)
                                return JsonResponse(data)   

                elif list_readtype[i] == 'SE':
                    r1 = item+'.fastq.gz'
                    r1op = item+'_R1.fastq.gz'
                    if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                        for j in set(reps):
                            if j == '1':
                                repname = mainname
                            else:
                                repname = '_'.join([mainname, j])   

                            r1 = repname+'.fastq.gz'
                            r1op = repname+'_R1.fastq.gz'
                            try:
                                if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                                    data['fastqerror'] = 'There is at least one library without fastq file ready. Please go to the setQC detail page.'
                                    return JsonResponse(data)
                            except Exception as e:
                                data['fastqerror'] = 'There is at least one library without fastq file ready. Please go to the setQC detail page.'
                                print(e)
                                return JsonResponse(data)

        i += 1

    if setinfo.experiment_type == 'ChIP-seq':
        for x in outinfo:
            if not x['seqinfo__read_type']:
                x['seqinfo__read_type'] = 'NA'
            if not x['seqinfo__machine__machine_name']:
                x['seqinfo__machine__machine_name'] = 'NA'
        writecontent = '\n'.join(['\t'.join([x['seqinfo__seq_id'], x['group_number'],
                                             str(x['is_input']
                                                 ), x['genome__genome_name'],
                                             x['label'], seqstatus[x['seqinfo__seq_id']],
                                             x['seqinfo__read_type'],
                                             x['seqinfo__libraryinfo__sampleinfo__sample_id'],
                                             x['seqinfo__libraryinfo__sampleinfo__species'],
                                             x['seqinfo__libraryinfo__experiment_type'],
                                             x['seqinfo__machine__machine_name'], setinfo.set_name]) for x in outinfo])

        featureheader = ['Library ID', 'Group ID',
                         'Is Input', 'Genome', 'Library Name', 'Processed Or Not',
                         'Read Type', 'Sample Name', 'Species',
                         'Experiment Type', 'Machine', 'Set Name']
        cmd1 = './utility/runSetQC_chipseq.sh ' + \
            setinfo.set_id + ' ' + request.user.email + \
            ' ' + re.sub(r"[\)\(]", ".", setinfo.set_name)
    else:
        # check if expirement is of type 10xATAC of each library:
        # 1. check if library passed has been process in cell ranger by looking for html output
        # 2. for libraries of same sample not processed with cell ranger-> create sample sheet for said libs

        # to process will hold 10x seqs
        to_process = {}

        # output_names will hold seqs that needs to be processed in cell ranger, will populate tsv file
        output_names = []
        to_process = Process10xRepsAndProcessList(outinfo, to_process)
        print(to_process)

        # check if name in output_names has been processed, if so strike it from list and
        # put processed flag
        #find genome used for samples
        if len(to_process) > 0:
            output_names = StrikeOutputNames(to_process, output_names)
            print('outputnames: ', output_names)
            print('to_process dict:', to_process)

        # find genome used for samples
            genome_dict = {}
            for x in outinfo:
                seqid = x['seqinfo__seq_id']
                genome_dict[seqid] = x['genome__genome_name']
            print(genome_dict)

        # make tsv file to be use as input for run10xPipeline script
            tsv_writecontent = '\n'.join(
                ['\t'.join([name, ','.join(to_process[name]), genome_dict[name]])
                 for name in output_names])

            print(tsv_writecontent)

        # sample sheet will be named: .Set_XXX_samplesheet.tsv
        # sample sheet will be located in SETQC_DIR
        # write .Set_XXX_samplesheet.tsv to setqcoutdir
            set_10x_input_file = os.path.join(
                setqcoutdir, '.'+setinfo.set_id+'_samplesheet.tsv')
            print('input 10xfile:', set_10x_input_file)
            if os.path.isfile(set_10x_input_file):
                data['setidexisterror'] = '.'+setinfo.set_id + \
                    ' \'s samplesheet is already existed. Do you want to override it and continue to run the pipeline and SetQC script?'
                print(data['setidexisterror'])
                return JsonResponse(data)
            try:
                with open(set_10x_input_file, 'w') as f:
                    f.write(tsv_writecontent)
            except Exception as e:
                data['writeseterror'] = 'Unexpected writing to Set_samplesheet.tsv Error!'

        # dict will map seq_info_id to if it has been 10xProcessed or not, even if not of 10xATAC
        tenXProcessed = {}
        to_process_keys = list(to_process.keys())
        for x in outinfo:
            if x['seqinfo__seq_id'] not in output_names and \
                    x['seqinfo__seq_id'] in to_process_keys:
                tenXProcessed[x['seqinfo__seq_id']] = 'Yes'
            else:
                tenXProcessed[x['seqinfo__seq_id']] = 'No'
        print('tenXProcessed: ', tenXProcessed)
        for x in outinfo:
            if not x['seqinfo__read_type']:
                x['seqinfo__read_type'] = 'NA'
            if not x['seqinfo__machine__machine_name']:
                x['seqinfo__machine__machine_name'] = 'NA'

        writecontent = '\n'.join(['\t'.join([x['seqinfo__seq_id'], x['genome__genome_name'],
                                             x['label'], seqstatus[x['seqinfo__seq_id']],
                                             x['seqinfo__read_type'],
                                             x['seqinfo__libraryinfo__sampleinfo__sample_id'],
                                             x['seqinfo__libraryinfo__sampleinfo__species'],
                                             x['seqinfo__libraryinfo__experiment_type'],
                                             x['seqinfo__machine__machine_name'], setinfo.set_name,
                                             tenXProcessed[x['seqinfo__seq_id']]]) for x in outinfo])
        featureheader = ['Library ID', 'Genome',
                         'Library Name', 'Processed Or Not', 'Read Type', 'Sample Name', 'Species',
                         'Experiment Type', 'Machine', 'Set Name', '10xProcessed']

        cmd1 = './utility/runSetQC.sh ' + setinfo.set_id + \
            ' ' + request.user.email + ' ' + \
            re.sub(r"[\)\(]", ".", setinfo.set_name)
   
    # write Set_**.txt to setqcoutdir
    setStatusFile = os.path.join(setqcoutdir, '.'+setinfo.set_id+'.txt')
    print(setStatusFile)
    if os.path.isfile(setStatusFile):
        data['setidexisterror'] = '.'+setinfo.set_id + \
            ' \'s report is already existed. Do you want to override it and continue to run the pipeline and SetQC script?'
        print(data['setidexisterror'])
        return JsonResponse(data)
    try:
        with open(setStatusFile, 'w') as f:
            f.write('\t'.join(featureheader)+'\n')
            f.write(writecontent)
    except Exception as e:
        data['writeseterror'] = 'Unexpected writing to Set.txt Error!'
    setinfo.status = 'JobSubmitted'
    setinfo.save()

    # run setQC script
    # cmd1 = './utility/runsetqctest.sh ' + setinfo.set_id + ' ' + request.user.email
    # print(cmd1)

    # cmd_tm = './utility/encode_test.sh .' + setinfo.set_id +'.txt'
    # print(cmd_tm)
    # log = open('some file.txt', 'a')
    # p = subprocess.Popen(cmd_tm, shell=True, stdout=log, stderr=log)

    print('running subprocess')
    p = subprocess.Popen(
        cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    data['writesetdone'] = 1
    return JsonResponse(data)


'''
This function will read each lib in set and check if 10xATAC exp. to process set up list for TSV sample sheet
Returns dict 
'''


def Process10xRepsAndProcessList(outinfo, to_process):
    for sequence in outinfo:
        if sequence['seqinfo__libraryinfo__experiment_type'] == '10xATAC':
            x = sequence['seqinfo__seq_id']
            print(f'seqinfo id: {x}')
            reps = []
            reps = reps + x.split('_')[2:]
            print(f'reps: {reps}')

            # check if seq being processed is original eg: bg_210<tab>bg_210<tab>genome
            if(len(reps) == 0):
                to_process[x] = [x]

            # new lib to process
            for rep in reps:

                if rep == '1':
                    to_insert = '_'.join(x.split('_')[:2])
                    if x in to_process.keys():
                        to_process[x].append(to_insert)
                    else:
                        to_process[x] = [to_insert]
                # new sequencing from same lib
                else:
                    to_insert = '_'.join(x.split('_')[:2]) + '_' + rep
                    if x in to_process.keys():
                        to_process[x].append(to_insert)
                    else:
                        to_process[x] = [to_insert]
    return(to_process)


'''
This function will check the libs present in output_names and of already processd then will strike it from 
list. If not already procesed will be kept 
'''


def StrikeOutputNames(to_process, output_names):
    tenxdir = settings.TENX_DIR
    output_names = list(to_process.keys())
    # check if output_names libs have been processed
    for name in output_names:
        tenx_output_folder = 'outs'
        tenx_target_outfile = 'web_summary.html'
        if not os.path.isdir(os.path.join(tenxdir, name)):
            print("not found: ")
            print(os.path.join(tenxdir, name))
        else:
            if not os.path.isfile(os.path.join(tenxdir, name,
                                               tenx_output_folder, tenx_target_outfile)):
                print("not found: ")
                print(os.path.join(tenxdir, name,
                                   tenx_output_folder, tenx_target_outfile))

            else:
                print('found: ', os.path.join(tenxdir, name))
                output_names.remove(name)
        print('outputnames: ', output_names)
        print('to_process dict:', to_process)
    return output_names


@transaction.atomic
def RunSetQC2(request, setqc_pk):
    libdir = settings.LIBQC_DIR
    fastqdir = settings.FASTQ_DIR
    setqcoutdir = settings.SETQC_DIR
    tenxdir = settings.TENX_DIR
    data = {}
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    if setinfo.requestor != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    allfolder = [fname for fname in os.listdir(
        libdir) if os.path.isdir(os.path.join(libdir, fname))]
    outinfo = list(LibraryInSet.objects.filter(librariesetqc=setinfo).
                   select_related('seqinfo__libraryinfo__sampleinfo', 'seqinfo__machine', 'genome').
                   values('seqinfo__seq_id', 'group_number', 'is_input', 'genome__genome_name',
                          'label', 'seqinfo__read_type', 'seqinfo__libraryinfo__sampleinfo__sample_id',
                          'seqinfo__libraryinfo__sampleinfo__species', 'seqinfo__libraryinfo__experiment_type',
                          'seqinfo__machine__machine_name').order_by('pk'))

    list1 = [x['seqinfo__seq_id'] for x in outinfo]
    list_readtype = [x['seqinfo__read_type'] for x in outinfo]
    seqstatus = {}
    i = 0
    for item in list1:
        if item not in allfolder:
            seqstatus[item] = 'No'
        else:
            if not os.path.isfile(os.path.join(libdir, item, '.finished.txt')):
                seqstatus[item] = 'No'
            else:
                seqstatus[item] = 'Yes'
        reps = ['1']
        reps = reps + item.split('_')[2:]
        mainname = '_'.join(item.split('_')[0:2])

        if seqstatus[item] == 'No':
            if not item.startswith('ENCODE_'):
                if list_readtype[i] == 'PE':
                    r1 = item+'_R1.fastq.gz'
                    r2 = item+'_R2.fastq.gz'
                    if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                        for j in set(reps):
                            if j == '1':
                                repname = mainname
                            else:
                                repname = '_'.join([mainname, j])   

                            r1 = repname+'_R1.fastq.gz'
                            r2 = repname+'_R2.fastq.gz'
                            try:
                                if not os.path.isfile(os.path.join(fastqdir, r1)) or not os.path.isfile(os.path.join(fastqdir, r2)):
                                    data['fastqerror'] = 'There is at least one library without fastq file. Please go to the setQC detail page.'
                                    return JsonResponse(data)
                            except Exception as e:
                                data['fastqerror'] = 'There is at least one library without fastq file ready. Please go to the setQC detail page.'
                                print(e)
                                return JsonResponse(data)   

                elif list_readtype[i] == 'SE':
                    r1 = item+'.fastq.gz'
                    r1op = item+'_R1.fastq.gz'
                    if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                        for j in set(reps):
                            if j == '1':
                                repname = mainname
                            else:
                                repname = '_'.join([mainname, j])   

                            r1 = repname+'.fastq.gz'
                            r1op = repname+'_R1.fastq.gz'
                            try:
                                if not os.path.isfile(os.path.join(fastqdir, r1)) and not os.path.isfile(os.path.join(fastqdir, r1op)):
                                    data['fastqerror'] = 'There is at least one library without fastq file ready. Please go to the setQC detail page.'
                                    return JsonResponse(data)
                            except Exception as e:
                                data['fastqerror'] = 'There is at least one library without fastq file ready. Please go to the setQC detail page.'
                                print(e)
                                return JsonResponse(data)
        i += 1

    if setinfo.experiment_type == 'ChIP-seq':
        for x in outinfo:
            if not x['seqinfo__read_type']:
                x['seqinfo__read_type'] = 'NA'
            if not x['seqinfo__machine__machine_name']:
                x['seqinfo__machine__machine_name'] = 'NA'

        writecontent = '\n'.join(['\t'.join([x['seqinfo__seq_id'], x['group_number'],
                                             str(x['is_input']
                                                 ), x['genome__genome_name'],
                                             x['label'], seqstatus[x['seqinfo__seq_id']
                                                                   ], x['seqinfo__read_type'],
                                             x['seqinfo__libraryinfo__sampleinfo__sample_id'],
                                             x['seqinfo__libraryinfo__sampleinfo__species'],
                                             x['seqinfo__libraryinfo__experiment_type'],
                                             x['seqinfo__machine__machine_name'], setinfo.set_name]) for x in outinfo])

        featureheader = ['Library ID', 'Group ID',
                         'Is Input', 'Genome', 'Library Name', 'Processed Or Not',
                         'Read Type', 'Sample Name', 'Species',
                         'Experiment Type', 'Machine', 'Set Name']
        cmd1 = './utility/runSetQC_chipseq.sh ' + \
            setinfo.set_id + ' ' + request.user.email + \
            ' ' + re.sub(r"[\)\(]", ".", setinfo.set_name)
    else:
        # check if expirement is of type 10xATAC of each library:
        # 1. check if library passed has been process in cell ranger by looking for html output
        # 2. for libraries of same sample not processed with cell ranger-> create sample sheet for said libs

        # to process will hold 10x seqs
        to_process = {}
        # output_names will hold seqs that needs to be processed in cell ranger, will populate tsv file
        output_names = []

        to_process = Process10xRepsAndProcessList(outinfo, to_process)
        print(to_process)

        # check if name in output_names has been processed, if so strike it from list and
        # put processed flag
        if len(to_process) > 0:
            output_names = StrikeOutputNames(to_process, output_names)
            print('outputnames: ', output_names)
            print('to_process dict:', to_process)

        # find genome used for samples
            genome_dict = {}
            for x in outinfo:
                seqid = x['seqinfo__seq_id']
                genome_dict[seqid] = x['genome__genome_name']
            print(genome_dict)

        # make tsv file to be use as input for run10xPipeline script
            tsv_writecontent = '\n'.join(
                ['\t'.join([name, ','.join(to_process[name]), genome_dict[name]])
                 for name in output_names])

            print(tsv_writecontent)

        # sample sheet will be named: .Set_XXX_samplesheet.tsv
        # sample sheet will be located in SETQC_DIR
        # write .Set_XXX_samplesheet.tsv to setqcoutdir
            set_10x_input_file = os.path.join(
                setqcoutdir, '.'+setinfo.set_id+'_samplesheet.tsv')
            print('input 10xfile:', set_10x_input_file)
            try:
                with open(set_10x_input_file, 'w') as f:
                    f.write(tsv_writecontent)
            except Exception as e:
                data['writeseterror'] = 'Unexpected writing to Set_samplesheet.tsv Error!'
        # dict will map seq_info_id to if it has been 10xProcessed or not, even if not of 10xATAC
        tenXProcessed = {}
        to_process_keys = list(to_process.keys())
        for x in outinfo:
            if x['seqinfo__seq_id'] not in output_names and \
                    x['seqinfo__seq_id'] in to_process_keys:
                tenXProcessed[x['seqinfo__seq_id']] = 'Yes'
            else:
                tenXProcessed[x['seqinfo__seq_id']] = 'No'
        # print(tenXProcessed)
        for x in outinfo:
            if not x['seqinfo__read_type']:
                x['seqinfo__read_type'] = 'NA'
            if not x['seqinfo__machine__machine_name']:
                x['seqinfo__machine__machine_name'] = 'NA'
        writecontent = '\n'.join(['\t'.join([x['seqinfo__seq_id'], x['genome__genome_name'],
                                             x['label'], seqstatus[x['seqinfo__seq_id']],
                                             x['seqinfo__read_type'],
                                             x['seqinfo__libraryinfo__sampleinfo__sample_id'],
                                             x['seqinfo__libraryinfo__sampleinfo__species'],
                                             x['seqinfo__libraryinfo__experiment_type'],
                                             x['seqinfo__machine__machine_name'], setinfo.set_name,
                                             tenXProcessed[x['seqinfo__seq_id']]]) for x in outinfo])
        featureheader = ['Library ID', 'Genome',
                         'Library Name', 'Processed Or Not', 'Read Type', 'Sample Name', 'Species',
                         'Experiment Type', 'Machine', 'Set Name', '10xProcessed']

        cmd1 = './utility/runSetQC.sh ' + setinfo.set_id + \
            ' ' + request.user.email + ' ' + \
            re.sub(r"[\)\(]", ".", setinfo.set_name)

    print('wc: ', writecontent)
    print('fh: ', featureheader)
    # write Set_**.txt to setqcoutdir
    setStatusFile = os.path.join(setqcoutdir, '.'+setinfo.set_id+'.txt')
    try:
        with open(setStatusFile, 'w') as f:
            f.write('\t'.join(featureheader)+'\n')
            f.write(writecontent)
    except Exception as e:
        data['writeseterror'] = 'Unexpected writing to Set.txt Error!'
    setinfo.status = 'JobSubmitted'
    setinfo.save()

    # run setQC script
    #cmd1 = './utility/runsetqctest.sh ' + setinfo.set_id + ' ' + request.user.email
    # print(cmd1)
    p = subprocess.Popen(
        cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data['writesetdone'] = 1
    return JsonResponse(data)


'''
This function will check what stage the pipeline is in and return it
'''


def TenXPipelineCheck(lib):
    seqstatus = ''
    tenx_output_folder = 'outs'
    tenx_target_outfile = 'web_summary.html'
    tenxdir = settings.TENX_DIR
    path = os.path.join(tenxdir, lib)
    # first check if there is an .inqueue then an .inprocess
    print('path: ', path)
    if not os.path.isdir(path):
        seqstatus = 'No'
    elif os.path.isfile(path + '/.inqueue'):
        seqstatus = 'In Queue'
    elif os.path.isfile(path + '/.inprocess'):
        seqstatus = 'In Process'
    elif os.path.isfile(path + '/_errors'):
        seqstatus = 'Error!'
    else:
        if not os.path.isfile(os.path.join(path,
                                           tenx_output_folder, tenx_target_outfile)):
            seqstatus = 'No'
        elif os.path.isfile(os.path.join(path, tenx_output_folder, tenx_target_outfile)):
            seqstatus = 'Yes'
        else:
            seqstatus = 'No'
    return seqstatus


def SetQCDetailView(request, setqc_pk):
    setinfo = get_object_or_404(LibrariesSetQC, pk=setqc_pk)
    libdir = settings.LIBQC_DIR
    fastqdir = settings.FASTQ_DIR
    tenxdir = settings.TENX_DIR
    allfolder = [fname for fname in os.listdir(
        libdir) if os.path.isdir(os.path.join(libdir, fname))]
    summaryfield = ['status', 'set_id', 'set_name', 'date_requested',
                    'requestor', 'experiment_type', 'notes', 'url', 'version']
    groupinputinfo = ''
    # librariesset = LibraryInSet.objects.filter(
    #     librariesetqc=setinfo).order_by('group_number', '-is_input')
    librariesset = LibraryInSet.objects.filter(
        librariesetqc=setinfo).order_by('pk')
    list1tem = list(librariesset.values_list('seqinfo', flat=True))
    list1 = [SeqInfo.objects.values_list(
        'seq_id', flat=True).get(id=x) for x in list1tem]

    list_readtype = [SeqInfo.objects.values_list(
        'read_type', flat=True).get(id=x) for x in list1tem]
    seqstatus = []
    fastqstatus = []
    list4 = [GenomeInfo.objects.values_list('genome_name', flat=True).get(
        id=x) for x in list(librariesset.values_list('genome', flat=True))]
    list5 = list(librariesset.values_list('label', flat=True))

    # need list of experiment types
    liblist = [SeqInfo.objects.values_list(
        'libraryinfo', flat=True).get(id=x) for x in list1tem]

    exp_type_list = [LibraryInfo.objects.values_list('experiment_type',
                                                     flat=True).get(id=x) for x in liblist]
    print("explist: ", exp_type_list)
    # need list for status of 10x expirments
    tenx_status = []

    if setinfo.collaborator != None:
        collab = setinfo.collaborator.first_name+' ' + \
            setinfo.collaborator.last_name+'('+setinfo.group.name+')'
    else:
        collab = ''
    i = 0
    for item in list1:
        # check if 10x experiment processed by checking summary.HTML file
        if exp_type_list[i] == '10xATAC':
            lib = item
            status = TenXPipelineCheck(lib)
            tenx_status.append(status)
        else:
            tenx_status.append('')

        if item not in allfolder:
            seqstatus.append('No')
        else:
            if not os.path.isfile(os.path.join(libdir, item, '.finished.txt')):
                seqstatus.append('No')
            else:
                seqstatus.append('Yes')

        if list_readtype[i] == 'PE':
            r1 = item+'_R1.fastq.gz'
            r2 = item+'_R2.fastq.gz'
            try:
                if os.path.isfile(os.path.join(fastqdir, r1)) and os.path.isfile(os.path.join(fastqdir, r2)):
                    fastqstatus.append('Yes')
                else:
                    fastqstatus.append('No')
            except Exception as e:
                fastqstatus.append('No')
                print(e)
        elif list_readtype[i] == 'SE':
            r1 = item+'.fastq.gz'
            try:
                if os.path.isfile(os.path.join(fastqdir, r1)):
                    fastqstatus.append('Yes')
                else:
                    fastqstatus.append('No')
            except Exception as e:
                fastqstatus.append('No')
                print(e)
        else:
            fastqstatus.append('PE or SE?')
        i += 1

    if setinfo.experiment_type == 'ChIP-seq':
        list2 = list(librariesset.values_list('group_number', flat=True))
        list3 = list(librariesset.values_list('is_input', flat=True))
        featureinfo = list(zip(list1, list_readtype, list2,
                               list3, list4, list5, fastqstatus, seqstatus))
        featureheader = ['Library ID', 'Read Type', 'Group ID',
                         'Is Input',  'Genome', 'Library Name', 'Has fastq', 'Processed']
    else:
        featureinfo = list(zip(list1, list_readtype, list4,
                               list5, fastqstatus, seqstatus, exp_type_list, tenx_status))
        featureheader = ['Library ID', 'Read Type',
                         'Genome', 'Library Name', 'Has fastq', 'Processed', 'TenX Processed']
    context = {
        'setinfo': setinfo,
        'summaryfield': summaryfield,
        'featureinfo': featureinfo,
        'featureheader': featureheader,
        'collab': collab
    }
    return render(request, 'setqc_app/details.html', context=context)


def load_users(request):
    q = request.GET.get('term', '')
    #collabusers = User.objects.filter(Q(first_name__icontains = q)|Q(last_name__icontains = q)).values('first_name','last_name')[:20]
    collabusers = User.objects.filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q))
    for f in Group.objects.filter(name__icontains=q):
        collabusers = collabusers | f.user_set.all()
    results = []
    for u in collabusers:
        uu = {}
        uu['id'] = str(u.id)+': '+u.first_name+' '+u.last_name + \
            '('+u.groups.all().first().name+')'
        uu['label'] = str(u.id)+': '+u.first_name+' ' + \
            u.last_name+'('+u.groups.all().first().name+')'
        uu['value'] = str(u.id)+': '+u.first_name+' ' + \
            u.last_name+'('+u.groups.all().first().name+')'
        results.append(uu)
    return JsonResponse(results, safe=False)


###
# TODO: do some error checking and exception raising
###
'''
This function opens and returns html webpage created by 10x ATAC pipeline for SETQC
@Requirements: the 10x webpage requested is softlinked in the BASE_DIR/data/websummary directory
'''


def tenx_output(request, setqc_pk, outputname):
    html = ('/'+outputname+"/outs/web_summary.html")
    tenxdir = settings.TENX_DIR
    file = open(tenxdir+html)

    data = file.read()
    if(data == None):
        print('No data read in 10x Web_Summary.html File!')
    return HttpResponse( data )

def tenx_output2(request, outputname):
    html=('/'+outputname+settings.TENX_WEBSUMMARY) 
    tenxdir = settings.TENX_DIR
    file = open(tenxdir+html)
    
    data = file.read()
    if(data == None):
        print('No data read in 10x Web_Summary.html File!')
    return HttpResponse( data )




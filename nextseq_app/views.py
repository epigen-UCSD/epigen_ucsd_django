import re
import csv
import os
import subprocess
import time
import shutil
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm, UserLoginForm, RunCreationForm, LibrariesInRunForm, SamplesToCreatForm
from django.views.generic import FormView, View
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from .models import Barcode, RunInfo, LibrariesInRun
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Q
from django.db import transaction
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core import serializers
from django.forms.models import model_to_dict
from setqc_app.forms import libraryparse
from masterseq_app.models import SeqInfo


def BarcodeDic():
    barcodes_dic = {}
    barcodes_list = Barcode.objects.all()
    for barcodes in barcodes_list:
        barcodes_dic[barcodes.indexid] = barcodes.indexseq
    return barcodes_dic


def UniqueValidation(tosavelist, existinglist):
    """ To test whether the item in the tosavelist has alreasy
    existed in the existinglist
    """
    return list(set(tosavelist).intersection(set(existinglist)))


def SelfUniqueValidation(tosavelist):
    """ To test whether there is duplicate in the supplied list
    """
    duplicate = []
    for i in range(0, len(tosavelist)):
        if tosavelist[i] in tosavelist[i+1:]:
            duplicate.append(tosavelist[i])
    return duplicate


def IndexValidation(i7list, i5list, fullorpartial):
    """ validate index in a run to be saved. It would return the duplicate
    index items if:
        (1). combinaton of i7 and i5 are the same, e.g. 
            lib1 with (i7 seq, i5 seq) as (AGTTCCGT,ATGTCAGA)
            lib2 with (i7 seq, i5 seq) as (AGTTCCGT,ATGTCAGA)

        (2). if partial match, for one with both of i7 and i5 applicable and one with only i7, 
        or both with only i7,  the i7 of one is part (including full part)of another, e.g
            lib1 with (i7 seq, i5 seq) as (AGTTCCGT,ATGTCAGA)
            lib2 with (i7 seq, i5 seq) as (AGTTCCG,'')

        (3). if full match, for one with both of i7 and i5 applicable and one with only i7, 
        or both with only i7,  the i7 is the same as another, e.g
            lib1 with (i7 seq, i5 seq) as (AGTTCCGT,ATGTCAGA)
            lib2 with (i7 seq, i5 seq) as (AGTTCCGT,'')
    """
    barcodes_dic = BarcodeDic()
    duplicate = []

    # prepare for the i7 seq and i5 seq from the index id
    combinelist = [x for x in list(zip(i7list, i5list)) if x[1]]
    print(combinelist)
    combinelistseq = [(barcodes_dic[x[0]], barcodes_dic[x[1]])
                      for x in combinelist]
    # validate index on case (1)
    for i in range(0, len(combinelistseq)):
        for j in range(i+1, len(combinelistseq)):
            if combinelistseq[i] == combinelistseq[j]:
                duplicate.append(
                    str(combinelist[i])+' vs '+str(combinelist[j]))

    combinei7 = list(set([x[0] for x in list(zip(i7list, i5list)) if x[1]]))
    combinei7seq = [barcodes_dic[x] for x in combinei7]
    singlei7 = [x[0] for x in list(zip(i7list, i5list)) if not x[1] and x[0]]
    singlei7seq = [barcodes_dic[x] for x in singlei7]

    # validate index on case (2)
    if fullorpartial == 'partial':
        for i in range(0, len(singlei7seq)):
            for j in range(i+1, len(singlei7seq)):
                if singlei7seq[i] in singlei7seq[j] or singlei7seq[j] in singlei7seq[i]:
                    duplicate.append(singlei7[i]+' vs '+singlei7[j])

        for i in range(0, len(combinei7seq)):
            for j in range(0, len(singlei7seq)):
                if combinei7seq[i] in singlei7seq[j] or singlei7seq[j] in combinei7seq[i]:
                    duplicate.append(combinei7[i]+' vs '+singlei7[j])

    # validate index on case (3)
    elif fullorpartial == 'full':
        for i in range(0, len(singlei7seq)):
            for j in range(i+1, len(singlei7seq)):
                if singlei7seq[i] == singlei7seq[j] or singlei7seq[j] == singlei7seq[i]:
                    duplicate.append(singlei7[i]+' vs '+singlei7[j])

        for i in range(0, len(combinei7seq)):
            for j in range(0, len(singlei7seq)):
                if combinei7seq[i] == singlei7seq[j] or singlei7seq[j] == combinei7seq[i]:
                    duplicate.append(combinei7[i]+' vs '+singlei7[j])


    return duplicate


def IndexView(request):
    """ View returns all runs those belong to the login user
    """

    RunInfo_list = RunInfo.objects.filter(
        operator=request.user).select_related('operator')
    return render(request, 'nextseq_app/userrunsinfo.html', {'RunInfo_list': RunInfo_list})


def AllRunsView(request):
    """ View returns all runs those in the database
    """
    RunInfo_list = RunInfo.objects.all().select_related('operator')
    context = {
        'RunInfo_list': RunInfo_list,
    }
    # only users in bioinformatics group can edit and delete all runs, even those not belong to him
    if not request.user.groups.filter(name='bioinformatics').exists():
        return render(request, 'nextseq_app/runsinfo.html', {'RunInfo_list': RunInfo_list})
    else:
        return render(request, 'nextseq_app/runsinfo_bio.html', {'RunInfo_list': RunInfo_list})


def AllSamplesView(request):
    """ View returns all libraries those in the runs
    """
    Samples_list = LibrariesInRun.objects.all().select_related(
        'singlerun', 'i7index', 'i5index')
    context = {
        'Samples_list': Samples_list,
    }
    return render(request, 'nextseq_app/samplesinfo.html', context)


def UserSamplesView(request):
    """ View returns all libraries those in the runs those belong to the login user
    """
    userruns = RunInfo.objects.filter(operator=request.user)
    Samples_list = LibrariesInRun.objects.filter(
        singlerun__in=userruns).select_related('singlerun', 'i7index', 'i5index')

    context = {
        'Samples_list': Samples_list,
    }
    return render(request, 'nextseq_app/usersamplesinfo.html', context)


class RunDetailView2(DetailView):
    """ View returns the detail informatin of a specific run, using Generic display views in Django
    """
    model = RunInfo
    template_name = 'nextseq_app/details.html'
    summaryfield = ['jobstatus', 'date', 'operator', 'machine', 'experiment_type', 'read_type', 'total_lanes', 'total_libraries', 'total_reads',
                    'percent_of_reads_demultiplexed', 'read_length', 'nextseqdir', 'extra_parameters']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['barcode'] = BarcodeDic()
        context['summaryfield'] = self.summaryfield
        return context


@transaction.atomic
def RunCreateView4(request):
    """ An unused and unmaintained view.
    View to add a new run, with one by one adding of libraries. 
    """
    run_form = RunCreationForm(request.POST or None)
    SamplesInlineFormSet = inlineformset_factory(RunInfo, LibrariesInRun, fields=[
                                                 'Library_ID', 'i7index', 'i5index'], extra=2)
    sample_formset = SamplesInlineFormSet(
        request.POST or None, instance=RunInfo())

    if run_form.is_valid():
        runinfo = run_form.save(commit=False)
        runinfo.operator = request.user
        sample_formset = SamplesInlineFormSet(request.POST, instance=runinfo)
        if sample_formset.is_valid():
            sample_formset.save(commit=False)
            Library_ID_list = []
            i7index_list = []
            i5index_list = []
            for form in sample_formset:
                if form not in sample_formset.deleted_forms:
                    # print(form.as_table())
                    try:
                        Library_ID_list.append(form.cleaned_data['Library_ID'])
                        i7index_list.append(form.cleaned_data['i7index'])
                        i5index_list.append(form.cleaned_data['i5index'])
                    except KeyError:
                        pass

            duplicate = IndexValidation(
                [x.indexid if x is not None else None for x in i7index_list],
                [x.indexid if x is not None else None for x in i5index_list],
                'partial'
            )
            if len(duplicate) > 0:
                context = {
                    'run_form': run_form,
                    'sample_formset': sample_formset,
                    'error_message': 'Duplicates:\t' + str(duplicate)

                }
                return render(request, 'nextseq_app/runandsamplesadd.html', context)

            runinfo.save()
            sample_formset.save()
            return redirect('nextseq_app:rundetail', pk=runinfo.id)

    return render(request, 'nextseq_app/runandsamplesadd.html', {'run_form': run_form, 'sample_formset': sample_formset})


@transaction.atomic
def RunCreateView6(request):
    """ View to add a new run, with bulk adding of libraries. 
    """

    run_form = RunCreationForm(
        request.POST or None, initial={'total_lanes': 1.00})
    # form to bulk add libraries
    form = SamplesToCreatForm(request.POST or None)

    if run_form.is_valid() and form.is_valid():
        runinfo = run_form.save(commit=False)
        runinfo.operator = request.user
        print(runinfo.experiment_type)
        sumlane = runinfo.total_lanes

        samplestocreat = form.cleaned_data['samplestocreat']
        tosave_list = []
        samplestocreat += '   \nSequencing_ID'  # mannually create a newline
        i7index_list = {}
        i5index_list = {}
        libraryid_list = []
        lanesum = 0
        samples_list = []
        nometa_list = []
        lane_blank_list = []
        data = {}

        for samples in samplestocreat.strip().split('\n'):
            samples_info = re.split(r'[\s]', samples+'  ')

            if samples != '\r' and samples_info[0] != 'Sequencing_ID':

                if samples_info[3]:
                    lane_tm = samples_info[3]
                else:
                    lane_tm = None

                # handle snATAC_v2, i7 in range(1-4), i5 in range(1-8)
                if runinfo.experiment_type == "S2":
                    try:
                        if samples_info[1] and samples_info[2]:
                            i7 = libraryparse(samples_info[1])
                            i5 = libraryparse(samples_info[2])
                            print(i7, i5)
                            # check ranges
                            if int(i7[0]) in range(1, 5) and int(i7[-1]) in range(1, 5) and int(i5[0]) in range(1, 9) and int(i5[-1]) in range(1, 9):
                                tosave_sample = LibrariesInRun(
                                    Library_ID=samples_info[0],
                                    i7index=Barcode.objects.get(
                                        indexid=','.join(i7)),
                                    i5index=Barcode.objects.get(
                                        indexid=','.join(i5)),
                                    lane=lane_tm,
                                )
                            else:
                                context = {
                                    'run_form': run_form,
                                    'form': form,
                                    'error_message': 'either both i7 not in range(1,4) or  i5 in range(1-8) for library input '+'\t'.join(samples_info)
                                }
                                return render(request, 'nextseq_app/runandsamplesbulkadd.html', context)

                        else:  # require 2 barcodes
                            context = {
                                'run_form': run_form,
                                'form': form,
                                'error_message': 'Need both i7 and i5 for snATAC for this library: '+'\t'.join(samples_info)
                            }
                            return render(request, 'nextseq_app/runandsamplesbulkadd.html', context)

                        if lane_tm not in i7index_list.keys():
                            i7index_list[lane_tm] = []
                            i5index_list[lane_tm] = []
                        i7index_list[lane_tm].append(samples_info[1])
                        i5index_list[lane_tm].append(samples_info[2])
                        libraryid_list.append(samples_info[0])

                    except ObjectDoesNotExist:
                        context = {
                            'run_form': run_form,
                            'form': form,
                            'error_message': 'There are indexes that are not stored in the database for this library: '+'\t'.join(samples_info)
                        }

                        return render(request, 'nextseq_app/runandsamplesbulkadd.html', context)

                    tosave_list.append(tosave_sample)
                # handle bulk barcodes
                else:
                    try:
                        if samples_info[1] and samples_info[2]:
                            tosave_sample = LibrariesInRun(
                                Library_ID=samples_info[0],
                                i7index=Barcode.objects.get(
                                    indexid=samples_info[1]),
                                i5index=Barcode.objects.get(
                                    indexid=samples_info[2]),
                                lane=lane_tm,
                            )
                        elif samples_info[1] and not samples_info[2]:
                            tosave_sample = LibrariesInRun(

                                Library_ID=samples_info[0],
                                i7index=Barcode.objects.get(
                                    indexid=samples_info[1]),
                                lane=lane_tm,
                            )
                        elif not samples_info[1] and samples_info[2]:
                            tosave_sample = LibrariesInRun(

                                Library_ID=samples_info[0],
                                i5index=Barcode.objects.get(
                                    indexid=samples_info[2]),
                                lane=lane_tm,
                            )
                        else:
                            tosave_sample = LibrariesInRun(

                                Library_ID=samples_info[0],
                                lane=lane_tm,
                            )
                        if lane_tm not in i7index_list.keys():
                            i7index_list[lane_tm] = []
                            i5index_list[lane_tm] = []
                        i7index_list[lane_tm].append(samples_info[1])
                        i5index_list[lane_tm].append(samples_info[2])
                        libraryid_list.append(samples_info[0])

                    except ObjectDoesNotExist:
                        context = {
                            'run_form': run_form,
                            'form': form,
                            'error_message': 'There are indexes that are not stored in the database for this library: '+'\t'.join(samples_info)
                        }

                        return render(request, 'nextseq_app/runandsamplesbulkadd.html', context)

                    tosave_list.append(tosave_sample)

                samples_list.append(samples_info[0])

        # library uniq validation.
        libraryselfduplicate = SelfUniqueValidation(libraryid_list)
        if len(libraryselfduplicate) > 0:

            context = {
                'run_form': run_form,
                'form': form,
                'error_message': 'Duplicate Library within this run:\t' + ';\t'.join(list(libraryselfduplicate))

            }
            return render(request, 'nextseq_app/runandsamplesbulkadd.html', context)

        existinglibray = list(
            LibrariesInRun.objects.values_list('Library_ID', flat=True))
        libraynotuniq = UniqueValidation(libraryid_list, existinglibray)

        # library uniq validation.
        if len(libraynotuniq) > 0:

            context = {
                'run_form': run_form,
                'form': form,
                'error_message': 'Libraries already exit:\t' + ';\t'.join(list(libraynotuniq))

            }
            return render(request, 'nextseq_app/runandsamplesbulkadd.html', context)

        # index validation.
        for ke in i7index_list.keys():
            if runinfo.experiment_type in ["TA", "TR", "TM"]:
                duplicate = IndexValidation(
                    i7index_list[ke], i5index_list[ke, 'full'])
            else:
                duplicate = IndexValidation(i7index_list[ke], i5index_list[ke], 'partial')
            if len(duplicate) > 0:
                context = {
                    'run_form': run_form,
                    'form': form,
                    'error_message': 'Duplicates:\t' + str(duplicate)

                }
                return render(request, 'nextseq_app/runandsamplesbulkadd.html', context)

        # handle portion of lane. The portion of lane of the library should be added in the metadata app first.
        for k in sorted(samples_list):
            try:
                this_seq = SeqInfo.objects.get(seq_id=k)
                if this_seq.portion_of_lane:
                    data[k] = {
                        'portion_of_lane': this_seq.portion_of_lane,
                    }
                    lanesum += this_seq.portion_of_lane
                else:
                    lane_blank_list.append(k)
            except ObjectDoesNotExist:
                nometa_list.append(k)

        if nometa_list:
            context = {
                'run_form': run_form,
                'form': form,
                'error_message': 'Not found in metadata app: '+','.join(nometa_list)+'. Please add them in metadata app first.'
            }
            return render(request, 'nextseq_app/runandsamplesbulkadd.html', context)

        if lane_blank_list:
            context = {
                'run_form': run_form,
                'form': form,
                'error_message': 'The portion of lane is blank of sequncings: '+','.join(lane_blank_list)+'. Please add them in metadata app first.'
            }
            return render(request, 'nextseq_app/runandsamplesbulkadd.html', context)

        # handle portion of lane. Pop up a detail messaage if the sum of the portion of lane is not equal to the input total lane
        if lanesum != sumlane:
            context = {
                'run_form': run_form,
                'form': form,
                'data': data,
                'modalshow': 1,
                'lanesum': lanesum,

            }
            return render(request, 'nextseq_app/runandsamplesbulkadd.html', context)

        runinfo.save()
        for samples in tosave_list:
            samples.singlerun = runinfo
        LibrariesInRun.objects.bulk_create(tosave_list)

        return redirect('nextseq_app:rundetail', pk=runinfo.id)

    context = {
        'run_form': run_form,
        'form': form,
    }

    return render(request, 'nextseq_app/runandsamplesbulkadd.html', context)


@transaction.atomic
def RunUpdateView2(request, username, run_pk):
    """ View to update an added run
    """

    runinfo = get_object_or_404(RunInfo, pk=run_pk)

    # only allow the owner of the run and the uses in bioinformatics group edit
    if runinfo.operator != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    run_form = RunCreationForm(request.POST or None, instance=runinfo)
    SamplesInlineFormSet = inlineformset_factory(RunInfo, LibrariesInRun, fields=[
        'Library_ID', 'i7index', 'i5index'], extra=3)
    sample_formset = SamplesInlineFormSet(
        request.POST or None, instance=runinfo)
    lanesum = 0
    data = {}
    lane_blank_list = []
    nometa_list = []

    if run_form.is_valid() and sample_formset.is_valid():
        runinfo = run_form.save(commit=False)
        sumlane = runinfo.total_lanes
        sample_formset.save(commit=False)
        Library_ID_list = []
        i7index_list = []
        i5index_list = []
        for form in sample_formset:
            if form not in sample_formset.deleted_forms:
                try:
                    Library_ID_list.append(form.cleaned_data['Library_ID'])
                    i7index_list.append(form.cleaned_data['i7index'])
                    i5index_list.append(form.cleaned_data['i5index'])
                except KeyError:
                    pass

        # library uniq validation
        libraryselfduplicate = SelfUniqueValidation(Library_ID_list)
        if len(libraryselfduplicate) > 0:

            context = {
                'run_form': run_form,
                'sample_formset': sample_formset,
                'runinfo': runinfo,
                'error_message': 'Duplicate Library within this run:\t' + ';\t'.join(list(libraryselfduplicate))

            }
            return render(request, 'nextseq_app/runandsamplesupdate.html', context)

        existinglibray = list(
            LibrariesInRun.objects.exclude(singlerun=runinfo).values_list('Library_ID', flat=True))
        libraynotuniq = UniqueValidation(Library_ID_list, existinglibray)

        if len(libraynotuniq) > 0:

            context = {
                'run_form': run_form,
                'sample_formset': sample_formset,
                'runinfo': runinfo,
                'error_message': 'Libraries already exit:\t' + ';\t'.join(list(libraynotuniq))

            }
            return render(request, 'nextseq_app/runandsamplesupdate.html', context)

        # index validation
        if runinfo.experiment_type in ["TA", "TR", "TM"]:
            duplicate = IndexValidation(
                [x.indexid if x is not None else None for x in i7index_list],
                [x.indexid if x is not None else None for x in i5index_list],
                'full'
            )
        else:
            duplicate = IndexValidation(
                [x.indexid if x is not None else None for x in i7index_list],
                [x.indexid if x is not None else None for x in i5index_list],
                'partial'

            )
        if len(duplicate) > 0:
            context = {
                'run_form': run_form,
                'sample_formset': sample_formset,
                'error_message': 'Duplicates:\t' + str(duplicate),
                'runinfo': runinfo,
            }
            return render(request, 'nextseq_app/runandsamplesupdate.html', context)

        # handle portion of lane. The portion of lane of the library should be added in the metadata app first.
        for k in sorted(Library_ID_list):
            try:
                this_seq = SeqInfo.objects.get(seq_id=k)
                if this_seq.portion_of_lane:
                    data[k] = {
                        'portion_of_lane': this_seq.portion_of_lane,
                    }
                    lanesum += this_seq.portion_of_lane
                else:
                    lane_blank_list.append(k)
            except ObjectDoesNotExist:
                nometa_list.append(k)

        if nometa_list:
            context = {
                'run_form': run_form,
                'sample_formset': sample_formset,
                'runinfo': runinfo,
                'error_message': 'Not found in metadata app: '+','.join(nometa_list)+'. Please add them in metadata app first.'
            }
            return render(request, 'nextseq_app/runandsamplesupdate.html', context)

        if lane_blank_list:
            context = {
                'run_form': run_form,
                'sample_formset': sample_formset,
                'runinfo': runinfo,
                'error_message': 'The portion of lane is blank of sequncings: '+','.join(lane_blank_list)+'. Please add them in metadata app first.'
            }
            return render(request, 'nextseq_app/runandsamplesupdate.html', context)

        if abs(lanesum-sumlane) > 1e-5:
            context = {
                'run_form': run_form,
                'sample_formset': sample_formset,
                'runinfo': runinfo,
                'data': data,
                'modalshow': 1,
                'lanesum': lanesum,

            }
            return render(request, 'nextseq_app/runandsamplesupdate.html', context)

        # Allow to resubmit the job when any field changed.
        if run_form.has_changed() or sample_formset.has_changed():
            runinfo.jobstatus = 'ClickToSubmit'

        runinfo.save()
        sample_formset.save()

        return redirect('nextseq_app:rundetail', pk=runinfo.pk)

    return render(request, 'nextseq_app/runandsamplesupdate.html', {'run_form': run_form, 'sample_formset': sample_formset, 'runinfo': runinfo})


def SampleSheetCreateView(request, run_pk):
    """ View to generate and download the samplesheet.csv file of a specific run. Located in the Run Detail page
    """

    runinfo = get_object_or_404(RunInfo, pk=run_pk)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="SampleSheet.csv"'
    writer = csv.writer(response, lineterminator=os.linesep)
    writer.writerow(['[Header]'])
    writer.writerow(['IEMFileVersion', '5'])
    writer.writerow(['Date', runinfo.date])
    writer.writerow(['Workflow', 'GenerateFASTQ'])
    writer.writerow(['Application', 'NextSeq FASTQ Only'])
    writer.writerow(['Instrument Type', 'NextSeq/MiniSeq'])
    writer.writerow(['Assay', 'Nextera XT / TruSeq LT'])
    writer.writerow(['Index Adapters', 'Nextera XT v2 Index Kit / TruSeq LT'])
    writer.writerow(['Description'])
    writer.writerow(['Chemistry', 'Amplicon'])
    writer.writerow([''])
    writer.writerow(['[Reads]'])
    a = runinfo.read_length.split('+')[0]
    if runinfo.read_type == 'PE':
        writer.writerow([a])
        writer.writerow([a])
    else:
        writer.writerow([a])
    writer.writerow([''])
    writer.writerow(['[Settings]'])
    writer.writerow([''])
    writer.writerow(['[Data]'])
    writer.writerow(['Sample_ID', 'Sample_Name', 'Sample_Plate', 'Sample_Well',
                     'I7_Index_ID', 'index', 'I5_Index_ID', 'index2', 'Sample_Project', 'Description'])
    samples_list = runinfo.librariesinrun_set.all()
    for samples in samples_list:
        i7id = samples.i7index or ''
        i5id = samples.i5index or ''
        i7seq = Barcode.objects.get(
            indexid=i7id).indexseq if i7id != '' else ''
        i5seq = Barcode.objects.get(
            indexid=i5id).indexseq if i5id != '' else ''
        writer.writerow([samples.Library_ID, '', '', '',
                         i7id, i7seq, i5id, i5seq, '', ''])
    return response


def RunDeleteView2(request, run_pk):
    """ View to delete a run. Only allow the owner and the members in bioinformatics group delete a run
    """

    deleterun = get_object_or_404(RunInfo, pk=run_pk)
    if deleterun.operator != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    deleterun.delete()
    return redirect('nextseq_app:userruns')

@transaction.atomic
def DemultiplexingView(request, run_pk):
    """ View to do the demutiplexing when user click to sumbit the job. Called by in epigen.js file:
    $(".dmpajax").on("click", function (e) 
    """
    print('started:'+str(run_pk))

    dmpdir = settings.NEXTSEQAPP_DMPDIR
    runinfo = get_object_or_404(RunInfo, pk=run_pk)
    tsccaccount = settings.TSCC_ACCOUNT

    if runinfo.operator != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    data = {}

    # to locate the flow cell run folder
    for fname in os.listdir(dmpdir):
        print(os.path.join(dmpdir, fname))
        if os.path.isdir(os.path.join(dmpdir, fname)) and fname.endswith(runinfo.Flowcell_ID):
            data['is_direxists'] = 1
            basedirname = os.path.join(dmpdir, fname)
            rundate = '20'+'-'.join([fname[i:i+2]
                                     for i in range(0, len(fname.split('_')[0]), 2)])
            break
    """ By default, the folder only be writable by the owner (zhc268). Modify the permission to 
    allow other users in the epigen-group to write in. Used when setting tscc account that run the
    pipeline as someone instead of zhc268
    """
    subprocess.call(['chmod', '-R', 'g+w', basedirname])

    """
     create folder Data/Fastqs. If folder already exits, it means it is not the first time to
     run the demultiplexing. A warning will pop up for the user to confirm(see mkdirerror2).
    """, 
    if 'is_direxists' in data:
        try:
            os.mkdir(os.path.join(basedirname, 'Data/Fastqs'))
        except FileNotFoundError as e:
            data['mkdirerror'] = 'Error: Folder: ' + \
                os.path.join(basedirname, 'Data')+' not exits'
            print(e)
            return JsonResponse(data)
        except FileExistsError as e:
            data['mkdirerror2'] = 'Error: Folder: ' + \
                os.path.join(basedirname, 'Data/Fastqs') + \
                ' already exists; \n Are you sure to continue and overwrite existed fastqs?'
            print(e)
            RunInfo.objects.filter(pk=run_pk).update(nextseqdir=basedirname)
            RunInfo.objects.filter(pk=run_pk).update(date=rundate)
            return JsonResponse(data)
        except Exception as e:
            data['mkdirerror'] = 'Unexpected mkdir .../Data/Fastqs Error!'
            print(e)
            return JsonResponse(data)

        # decide if mixed two primers with one primer
        samples_list = runinfo.librariesinrun_set.all()
        i7len = len(
            [x for x in samples_list.values_list('i7index', flat=True) if x])
        i5len = len(
            [x for x in samples_list.values_list('i5index', flat=True) if x])
        if i7len == i5len or i5len == 0:
            towritefiles = [os.path.join(
                basedirname, 'Data/Fastqs', 'SampleSheet.csv')]
        else:
            try:
                os.mkdir(os.path.join(basedirname, 'Data/Fastqs/OnePrimer'))
            except Exception as e:
                data['mkdirerror'] = 'Unexpected mkdir .../Data/Fastqs/OnePrimer Error!'
                print(e)
                return JsonResponse(data)
            try:
                os.mkdir(os.path.join(basedirname, 'Data/Fastqs/TwoPrimers'))
            except Exception as e:
                data['mkdirerror'] = 'Unexpected mkdir .../Data/Fastqs/TwoPrimers Error!'
                print(e)
                return JsonResponse(data)
            towritefiles = [os.path.join(basedirname, 'Data/Fastqs/OnePrimer', 'SampleSheet.csv'),
                            os.path.join(basedirname, 'Data/Fastqs/TwoPrimers', 'SampleSheet.csv')]
        try:
            for filename in towritefiles:
                if runinfo.experiment_type == 'S2':
                    i1_file = open(filename.replace('.csv', '_I1.csv'), 'w')
                    i2_file = open(filename.replace('.csv', '_I2.csv'), 'w')
                # support for sc-RNA expts.
                elif runinfo.experiment_type in ['TA', 'TR', 'TM']:
                    i1_file = open(filename.replace('.csv', '_I1.csv'), 'w')
                    i1_file.write(','.join(["Lane", "Sample", "Index"])+'\n')

                # generate the samplesheet.csv file and put it under the runfolder
                with open(filename, 'w') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['[Header]'])
                    writer.writerow(['IEMFileVersion', '5'])
                    writer.writerow(['Date', rundate])
                    writer.writerow(['Workflow', 'GenerateFASTQ'])
                    writer.writerow(['Application', 'NextSeq FASTQ Only'])
                    writer.writerow(['Instrument Type', 'NextSeq/MiniSeq'])
                    writer.writerow(['Assay', 'Nextera XT / TruSeq LT'])
                    writer.writerow(
                        ['Index Adapters', 'Nextera XT v2 Index Kit / TruSeq LT'])
                    writer.writerow(['Description'])
                    writer.writerow(['Chemistry', 'Amplicon'])
                    writer.writerow([''])
                    writer.writerow(['[Reads]'])
                    a = runinfo.read_length.split('+')[0]
                    if runinfo.read_type == 'PE':
                        writer.writerow([a])
                        writer.writerow([a])
                    else:
                        writer.writerow([a])
                    writer.writerow([''])
                    writer.writerow(['[Settings]'])
                    writer.writerow([''])
                    writer.writerow(['[Data]'])
                    writer.writerow(['Sample_ID', 'Sample_Name', 'Sample_Plate', 'Sample_Well',
                                     'I7_Index_ID', 'index', 'I5_Index_ID', 'index2', 'Sample_Project', 'Description'])
                    samples_list = runinfo.librariesinrun_set.all()
                    for samples in samples_list:
                        if filename == os.path.join(basedirname, 'Data/Fastqs', 'SampleSheet.csv'):
                            i7id = samples.i7index or ''
                            i5id = samples.i5index or ''
                            i7seq = Barcode.objects.get(
                                indexid=i7id).indexseq if i7id != '' else ''
                            i5seq = Barcode.objects.get(
                                indexid=i5id).indexseq if i5id != '' else ''
                            writer.writerow(
                                [samples.Library_ID, '', '', '', i7id, i7seq, i5id, i5seq, '', ''])

                            # handle snATAC
                            if runinfo.experiment_type == 'S2':
                                i1_file.write(i7seq+'\n')
                                i2_file.write(i5seq+'\n')
                            elif runinfo.experiment_type in ['TA', 'TR', 'TM']:
                                i1_file.write(
                                    ','.join(['*', samples.Library_ID, i7id.indexid])+'\n')
                        else:
                            if not samples.i5index:
                                if filename == os.path.join(basedirname, 'Data/Fastqs/OnePrimer', 'SampleSheet.csv'):
                                    i7id = samples.i7index or ''
                                    i7seq = Barcode.objects.get(
                                        indexid=i7id).indexseq if i7id != '' else ''
                                    writer.writerow(
                                        [samples.Library_ID, '', '', '', i7id, i7seq, '', '', '', ''])
                            else:
                                if filename == os.path.join(basedirname, 'Data/Fastqs/TwoPrimers', 'SampleSheet.csv'):
                                    i7id = samples.i7index or ''
                                    i5id = samples.i5index or ''
                                    i7seq = Barcode.objects.get(
                                        indexid=i7id).indexseq if i7id != '' else ''
                                    i5seq = Barcode.objects.get(
                                        indexid=i5id).indexseq if i5id != '' else ''
                                    writer.writerow(
                                        [samples.Library_ID, '', '', '', i7id, i7seq, i5id, i5seq, '', ''])
                if runinfo.experiment_type == 'S2':
                    i1_file.close()
                    i2_file.close()
                elif runinfo.experiment_type in ['TA', 'TR', 'TM']:
                    i1_file.close()

        except Exception as e:
            data['writesamplesheeterror'] = 'Unexpected writing to SampleSheet.csv Error!'
            print(e)
            return JsonResponse(data)

        RunInfo.objects.filter(pk=run_pk).update(nextseqdir=basedirname)
        RunInfo.objects.filter(pk=run_pk).update(date=rundate)
        RunInfo.objects.filter(pk=run_pk).update(jobstatus='JobSubmitted')

        # runBcl2fastq
        print('expt type: %s. Flowcell ID: %s' %
              (runinfo.experiment_type, runinfo.Flowcell_ID))
        if runinfo.experiment_type == 'S2':
            cmd1 = './utility/runDemuxSnATAC.sh ' + runinfo.Flowcell_ID + \
                ' ' + basedirname + ' ' + request.user.email + ' ' + tsccaccount
        elif runinfo.experiment_type == 'TA':
            # write extra_parameters to disk
            with open(os.path.join(basedirname, 'Data/Fastqs/', 'extraPars.txt'), 'w') as out:
                out.write(runinfo.extra_parameters)

            cmd1 = './utility/runDemux10xATAC.sh ' + runinfo.Flowcell_ID + \
                ' ' + basedirname + ' ' + request.user.email + ' ' + tsccaccount
        elif runinfo.experiment_type == 'TR':
            # write extra_parameters to disk
            with open(os.path.join(basedirname, 'Data/Fastqs/', 'extraPars.txt'), 'w') as out:
                out.write(runinfo.extra_parameters)
            cmd1 = './utility/runDemux10xRNA.sh ' + runinfo.Flowcell_ID + \
                ' ' + basedirname + ' ' + request.user.email + ' ' + tsccaccount
        elif runinfo.experiment_type == 'TM':
            # write extra_parameters to disk
            print("TM")
            with open(os.path.join(basedirname, 'Data/Fastqs/', 'extraPars.txt'), 'w') as out:
                out.write(runinfo.extra_parameters)
            cmd1 = './utility/runDemux10xATAC_RNA.sh ' + runinfo.Flowcell_ID + \
                ' ' + basedirname + ' ' + request.user.email + ' ' + tsccaccount

        else:
            cmd1 = './utility/runBcl2fastq.sh ' + runinfo.Flowcell_ID + \
                ' ' + basedirname + ' ' + request.user.email + ' ' + tsccaccount
        print(cmd1)

        p = subprocess.Popen(cmd1, shell=True)
        # thisjobid=p.pid

        data['writetosamplesheet'] = 1
        data['updatedate'] = '/'.join([rundate.split('-')[i]
                                       for i in [1, 2, 0]])
        return JsonResponse(data)

    else:
        return JsonResponse(data)


@transaction.atomic
def DemultiplexingView2(request, run_pk):
    """ View to do the demutiplexing when user click to rerun the job. Called by epigen.js file:
    $(".dmpajax").on("click", function (e) , when mkdirerror2 (Data/Fastqs already exist) occurs.
    TO do: considering merging this view with the DemultiplexingView view as one view

    """

    dmpdir = settings.NEXTSEQAPP_DMPDIR
    runinfo = get_object_or_404(RunInfo, pk=run_pk)
    tsccaccount = settings.TSCC_ACCOUNT
    if runinfo.operator != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    data = {}

    # locate the flow cell run folder
    for fname in os.listdir(dmpdir):
        if os.path.isdir(os.path.join(dmpdir, fname)) and fname.endswith(runinfo.Flowcell_ID):
            data['is_direxists'] = 1
            basedirname = os.path.join(dmpdir, fname)
            rundate = '20'+'-'.join([fname[i:i+2]
                                     for i in range(0, len(fname.split('_')[0]), 2)])
            break

    """ By default, the folder only be writable by the owner (zhc268). Modify the permission to 
    allow other users in the epigen-group to write in. Used when setting tscc account that run the
    pipeline as someone instead of zhc268
    """
    subprocess.call(['chmod', '-R', 'g+w', basedirname])

    if 'is_direxists' in data:
        samples_list = runinfo.librariesinrun_set.all()

        i7len = len(
            [x for x in samples_list.values_list('i7index', flat=True) if x])
        i5len = len(
            [x for x in samples_list.values_list('i5index', flat=True) if x])
        if i7len == i5len or i5len == 0:
            towritefiles = [os.path.join(
                basedirname, 'Data/Fastqs', 'SampleSheet.csv')]
        else:
            os.makedirs(os.path.join(
                basedirname, 'Data/Fastqs/OnePrimer'), exist_ok=True)
            os.makedirs(os.path.join(
                basedirname, 'Data/Fastqs/TwoPrimers'), exist_ok=True)
            towritefiles = [os.path.join(basedirname, 'Data/Fastqs/OnePrimer', 'SampleSheet.csv'),
                            os.path.join(basedirname, 'Data/Fastqs/TwoPrimers', 'SampleSheet.csv')]
        try:
            for filename in towritefiles:
                if runinfo.experiment_type == 'S2':
                    i1_file = open(filename.replace('.csv', '_I1.csv'), 'w')
                    i2_file = open(filename.replace('.csv', '_I2.csv'), 'w')
                elif runinfo.experiment_type in ['TA', 'TR', 'TM']:
                    i1_file = open(filename.replace('.csv', '_I1.csv'), 'w')
                    i1_file.write(','.join(["Lane", "Sample", "Index"])+'\n')

                # generate the samplesheet.csv file and put it under the runfolder
                with open(filename, 'w') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['[Header]'])
                    writer.writerow(['IEMFileVersion', '5'])
                    writer.writerow(['Date', rundate])
                    writer.writerow(['Workflow', 'GenerateFASTQ'])
                    writer.writerow(['Application', 'NextSeq FASTQ Only'])
                    writer.writerow(['Instrument Type', 'NextSeq/MiniSeq'])
                    writer.writerow(['Assay', 'Nextera XT / TruSeq LT'])
                    writer.writerow(
                        ['Index Adapters', 'Nextera XT v2 Index Kit / TruSeq LT'])
                    writer.writerow(['Description'])
                    writer.writerow(['Chemistry', 'Amplicon'])
                    writer.writerow([''])
                    writer.writerow(['[Reads]'])
                    a = runinfo.read_length.split('+')[0]
                    if runinfo.read_type == 'PE':
                        writer.writerow([a])
                        writer.writerow([a])
                    else:
                        writer.writerow([a])
                    writer.writerow([''])
                    writer.writerow(['[Settings]'])
                    writer.writerow([''])
                    writer.writerow(['[Data]'])
                    writer.writerow(['Sample_ID', 'Sample_Name', 'Sample_Plate', 'Sample_Well',
                                     'I7_Index_ID', 'index', 'I5_Index_ID', 'index2', 'Sample_Project', 'Description'])
                    samples_list = runinfo.librariesinrun_set.all()
                    for samples in samples_list:
                        if filename == os.path.join(basedirname, 'Data/Fastqs', 'SampleSheet.csv'):
                            i7id = samples.i7index or ''
                            i5id = samples.i5index or ''
                            i7seq = Barcode.objects.get(
                                indexid=i7id).indexseq if i7id != '' else ''
                            i5seq = Barcode.objects.get(
                                indexid=i5id).indexseq if i5id != '' else ''
                            writer.writerow(
                                [samples.Library_ID, '', '', '', i7id, i7seq, i5id, i5seq, '', ''])

                            # handle snATAC
                            if runinfo.experiment_type == 'S2':
                                i1_file.write(i7seq+'\n')
                                i2_file.write(i5seq+'\n')
                            elif runinfo.experiment_type in ['TA', 'TR', 'TM']:
                                i1_file.write(
                                    ','.join(['*', samples.Library_ID, i7id.indexid]) + '\n')

                        else:
                            if not samples.i5index:
                                if filename == os.path.join(basedirname, 'Data/Fastqs/OnePrimer', 'SampleSheet.csv'):
                                    i7id = samples.i7index or ''
                                    i7seq = Barcode.objects.get(
                                        indexid=i7id).indexseq if i7id != '' else ''
                                    writer.writerow(
                                        [samples.Library_ID, '', '', '', i7id, i7seq, '', '', '', ''])
                            else:
                                if filename == os.path.join(basedirname, 'Data/Fastqs/TwoPrimers', 'SampleSheet.csv'):
                                    i7id = samples.i7index or ''
                                    i5id = samples.i5index or ''
                                    i7seq = Barcode.objects.get(
                                        indexid=i7id).indexseq if i7id != '' else ''
                                    i5seq = Barcode.objects.get(
                                        indexid=i5id).indexseq if i5id != '' else ''
                                    writer.writerow(
                                        [samples.Library_ID, '', '', '', i7id, i7seq, i5id, i5seq, '', ''])

                if runinfo.experiment_type == 'S2':
                    i1_file.close()
                    i2_file.close()
                elif runinfo.experiment_type in ["TA", 'TR', "TM"]:
                    i1_file.close()
        except Exception as e:
            data['writesamplesheeterror'] = 'Unexpected writing to SampleSheet.csv Error!'
            print(e)
            return JsonResponse(data)

        RunInfo.objects.filter(pk=run_pk).update(nextseqdir=basedirname)
        RunInfo.objects.filter(pk=run_pk).update(date=rundate)
        RunInfo.objects.filter(pk=run_pk).update(jobstatus='JobSubmitted')

        # runBcl2fastq
        if runinfo.experiment_type == 'S2':
            cmd1 = './utility/runDemuxSnATAC.sh ' + runinfo.Flowcell_ID + \
                ' ' + basedirname + ' ' + request.user.email + ' ' + tsccaccount
        elif runinfo.experiment_type == 'TA':
            # write extra_parameters to disk
            with open(os.path.join(basedirname, 'Data/Fastqs/', 'extraPars.txt'), 'w') as out:
                out.write(runinfo.extra_parameters)

            cmd1 = './utility/runDemux10xATAC.sh ' + runinfo.Flowcell_ID + \
                ' ' + basedirname + ' ' + request.user.email + ' ' + tsccaccount
        elif runinfo.experiment_type == 'TR':
            # write extra_parameters to disk
            with open(os.path.join(basedirname, 'Data/Fastqs/', 'extraPars.txt'), 'w') as out:
                out.write(runinfo.extra_parameters)
            cmd1 = 'bash ./utility/runDemux10xRNA.sh ' + runinfo.Flowcell_ID + \
                ' ' + basedirname + ' ' + request.user.email + ' ' + tsccaccount
        elif runinfo.experiment_type == 'TM':
            # write extra_parameters to disk
            with open(os.path.join(basedirname, 'Data/Fastqs/', 'extraPars.txt'), 'w') as out:
                out.write(runinfo.extra_parameters)
            cmd1 = './utility/runDemux10xATAC_RNA.sh ' + runinfo.Flowcell_ID + \
                ' ' + basedirname + ' ' + request.user.email + ' ' + tsccaccount
        else:
            cmd1 = './utility/runBcl2fastq.sh ' + runinfo.Flowcell_ID + \
                ' ' + basedirname + ' ' + request.user.email + ' ' + tsccaccount
        print(cmd1)
        p = subprocess.Popen(cmd1, shell=True)
        # thisjobid=p.pid

        data['writetosamplesheet'] = 1
        data['updatedate'] = '/'.join([rundate.split('-')[i]
                                       for i in [1, 2, 0]])
        return JsonResponse(data)

    else:
        return JsonResponse(data)


@transaction.atomic
def DownloadingfromIGM(request, run_pk):
    """ View to download fastq files from IGM  when user click to transfer data (the button is the 
    same place with that do demultiplexing). Called by epigen.js file:
    (".downloadajax").on("click", function (e)

    """

    runinfo = get_object_or_404(RunInfo, pk=run_pk)
    ftp_addr = request.POST.get("downloadaddress")
    ftp_user = request.POST.get("username")
    ftp_password = request.POST.get("pass")
    tsccaccount = settings.TSCC_ACCOUNT

    data = {}
    try:
        fullname = ftp_addr.strip("/").split("/")
        fastq_dir = os.path.join(
            '/projects/ps-epigen/seqdata', fullname[-2], fullname[-1])
        rundate = fullname[-1].split('_')[0]
        if len(rundate) != 6 or not rundate.isdigit():
            data['parseerror'] = 'Date parse error!'
            return JsonResponse(data)

        rundatefinal = '20' + \
            '-'.join([rundate[i:i+2]
                      for i in range(0, len(rundate.split('_')[0]), 2)])
        flowname = fullname[-1].split('_')[3][1:]
    except Exception as e:
        data['parseerror'] = 'Date and Flowcell_ID parse error!'
        print(e)
        return JsonResponse(data)
    if RunInfo.objects.exclude(pk=run_pk).filter(Flowcell_ID=flowname).exists():
        data['flowduperror'] = 'Flowcell_ID with name: ' + \
            flowname+'is already existed.'
        return JsonResponse(data)
    RunInfo.objects.filter(pk=run_pk).update(date=rundatefinal)
    RunInfo.objects.filter(pk=run_pk).update(Flowcell_ID=flowname)
    RunInfo.objects.filter(pk=run_pk).update(jobstatus='JobSubmitted')
    RunInfo.objects.filter(pk=run_pk).update(nextseqdir=fastq_dir)

    data['updatedate'] = rundatefinal
    data['flowid'] = flowname
    cmd = "./utility/download_igm.sh {0} {1} {2} {3} {4} {5}".format(
        ftp_addr, ftp_user, ftp_password, flowname, request.user.email, tsccaccount)
    print(cmd)
    p = subprocess.Popen(cmd,
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return JsonResponse(data)

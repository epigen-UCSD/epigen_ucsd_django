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


def BarcodeDic():
    barcodes_dic = {}
    barcodes_list = Barcode.objects.all()
    for barcodes in barcodes_list:
        barcodes_dic[barcodes.indexid] = barcodes.indexseq
    return barcodes_dic


def UniqueValidation(tosavelist, existinglist):
    return list(set(tosavelist).intersection(set(existinglist)))


def SelfUniqueValidation(tosavelist):
    duplicate = []
    for i in range(0, len(tosavelist)):
        if tosavelist[i] in tosavelist[i+1:]:
            duplicate.append(tosavelist[i])
    return duplicate


def IndexValidation(i7list, i5list):
    barcodes_dic = BarcodeDic()
    duplicate = []

    combinelist = [x for x in list(zip(i7list, i5list)) if x[1]]
    print(combinelist)
    combinelistseq = [(barcodes_dic[x[0]], barcodes_dic[x[1]])
                      for x in combinelist]
    for i in range(0, len(combinelistseq)):
        for j in range(i+1, len(combinelistseq)):
            if combinelistseq[i] == combinelistseq[j]:
                duplicate.append(
                    str(combinelist[i])+' vs '+str(combinelist[j]))

    combinei7 = list(set([x[0] for x in list(zip(i7list, i5list)) if x[1]]))
    combinei7seq = [barcodes_dic[x] for x in combinei7]
    singlei7 = [x[0] for x in list(zip(i7list, i5list)) if not x[1] and x[0]]
    singlei7seq = [barcodes_dic[x] for x in singlei7]

    for i in range(0, len(singlei7seq)):
        for j in range(i+1, len(singlei7seq)):
            if singlei7seq[i] in singlei7seq[j] or singlei7seq[j] in singlei7seq[i]:
                duplicate.append(singlei7[i]+' vs '+singlei7[j])

    for i in range(0, len(combinei7seq)):
        for j in range(0, len(singlei7seq)):
            if combinei7seq[i] in singlei7seq[j] or singlei7seq[j] in combinei7seq[i]:
                duplicate.append(combinei7[i]+' vs '+singlei7[j])

    return duplicate


def IndexView(request):

    RunInfo_list = RunInfo.objects.filter(operator=request.user)
    return render(request, 'nextseq_app/userrunsinfo.html', {'RunInfo_list': RunInfo_list})


class HomeView(ListView):
    template_name = "nextseq_app/runsinfo.html"
    context_object_name = 'RunInfo_list'

    def get_queryset(self):
        queryset_list = RunInfo.objects.all()
        if self.request.GET.get('q'):
            q = self.request.GET.get('q')
            # print(q)
            queryset_list = queryset_list.filter(
                Q(operator__username__icontains=q) |
                Q(Flowcell_ID__icontains=q) |
                Q(read_type__icontains=q) |
                Q(read_length__icontains=q)

            ).distinct()

        return queryset_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['number'] = self.get_queryset().count()
        return context


def AllSamplesView(request):
    Samples_list = LibrariesInRun.objects.all()
    barcodes_dic = BarcodeDic()
    number = LibrariesInRun.objects.count()

    context = {
        'Samples_list': Samples_list,
        'barcode': barcodes_dic,
        'number': number

    }
    return render(request, 'nextseq_app/samplesinfo.html', context)


def UserSamplesView(request):
    userruns = RunInfo.objects.filter(operator=request.user)
    Samples_list = LibrariesInRun.objects.filter(singlerun__in=userruns)
    barcodes_dic = BarcodeDic()
    usersamples = True

    context = {
        'Samples_list': Samples_list,
        'barcode': barcodes_dic,
        'usersamples': usersamples
    }
    return render(request, 'nextseq_app/usersamplesinfo.html', context)


class RunDetailView2(DetailView):
    model = RunInfo
    template_name = 'nextseq_app/details.html'
    summaryfield = ['jobstatus', 'date', 'operator', 'read_type', 'total_libraries', 'total_reads',
                    'percent_of_reads_demultiplexed', 'read_length', 'nextseqdir']
    # object = FooForm(data=model_to_dict(Foo.objects.get(pk=object_id)))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['barcode'] = barcodes_dic
        context['barcode'] = BarcodeDic()
        context['summaryfield'] = self.summaryfield
        return context


@transaction.atomic
def RunCreateView4(request):
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
                [x.indexid if x is not None else None for x in i5index_list]
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
    run_form = RunCreationForm(request.POST or None)
    form = SamplesToCreatForm(request.POST or None)

    if run_form.is_valid() and form.is_valid():
        runinfo = run_form.save(commit=False)
        runinfo.operator = request.user
        print(runinfo.experiment_type)

        samplestocreat = form.cleaned_data['samplestocreat']
        tosave_list = []
        samplestocreat += '   \nLibrary_ID'
        i7index_list = []
        i5index_list = []
        libraryid_list = []
        for samples in samplestocreat.strip().split('\n'):
            samples_info = re.split(r'[\s]', samples)

            # handle snATAC_v2, i7 in range(1-4), i5 in range(1-8)
            if runinfo.experiment_type == "S2" and samples != '\r' and samples_info[0] != 'Library_ID':
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

                    i7index_list.append(','.join(i7))
                    i5index_list.append(','.join(i5))
                    libraryid_list.append(samples_info[0])

                except ObjectDoesNotExist:
                    context = {
                        'run_form': run_form,
                        'form': form,
                        'error_message': 'There are indexes that are not stored in the database for this library: '+'\t'.join(samples_info)
                    }

                    return render(request, 'nextseq_app/runandsamplesbulkadd.html', context)

                tosave_list.append(tosave_sample)

            # hand bulk barcodes
            if runinfo.experiment_type in ["BK", "TA"] and samples != '\r' and samples_info[0] != 'Library_ID':
                try:
                    if samples_info[1] and samples_info[2]:
                        tosave_sample = LibrariesInRun(
                            Library_ID=samples_info[0],
                            i7index=Barcode.objects.get(
                                indexid=samples_info[1]),
                            i5index=Barcode.objects.get(
                                indexid=samples_info[2]),
                        )
                    elif samples_info[1] and not samples_info[2]:
                        tosave_sample = LibrariesInRun(

                            Library_ID=samples_info[0],
                            i7index=Barcode.objects.get(
                                indexid=samples_info[1]),
                        )
                    elif not samples_info[1] and samples_info[2]:
                        tosave_sample = LibrariesInRun(

                            Library_ID=samples_info[0],
                            i5index=Barcode.objects.get(
                                indexid=samples_info[2]),
                        )
                    else:
                        tosave_sample = LibrariesInRun(

                            Library_ID=samples_info[0],
                        )

                    i7index_list.append(samples_info[1])
                    i5index_list.append(samples_info[2])
                    libraryid_list.append(samples_info[0])

                except ObjectDoesNotExist:
                    context = {
                        'run_form': run_form,
                        'form': form,
                        'error_message': 'There are indexes that are not stored in the database for this library: '+'\t'.join(samples_info)
                    }

                    return render(request, 'nextseq_app/runandsamplesbulkadd.html', context)

                tosave_list.append(tosave_sample)

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

        if len(libraynotuniq) > 0:

            context = {
                'run_form': run_form,
                'form': form,
                'error_message': 'Libraries already exit:\t' + ';\t'.join(list(libraynotuniq))

            }
            return render(request, 'nextseq_app/runandsamplesbulkadd.html', context)

        duplicate = IndexValidation(i7index_list, i5index_list)
        if len(duplicate) > 0:

            context = {
                'run_form': run_form,
                'form': form,
                'error_message': 'Duplicates:\t' + str(duplicate)

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
    runinfo = get_object_or_404(RunInfo, pk=run_pk)
    if runinfo.operator != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    run_form = RunCreationForm(request.POST or None, instance=runinfo)
    SamplesInlineFormSet = inlineformset_factory(RunInfo, LibrariesInRun, fields=[
        'Library_ID', 'i7index', 'i5index'], extra=3)
    sample_formset = SamplesInlineFormSet(
        request.POST or None, instance=runinfo)

    if run_form.is_valid() and sample_formset.is_valid():
        runinfo = run_form.save(commit=False)
        # runinfo.operator = request.user
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

        duplicate = IndexValidation(
            [x.indexid if x is not None else None for x in i7index_list],
            [x.indexid if x is not None else None for x in i5index_list]
        )
        if len(duplicate) > 0:
            context = {
                'run_form': run_form,
                'sample_formset': sample_formset,
                'error_message': 'Duplicates:\t' + str(duplicate),
                'runinfo': runinfo,

            }
            return render(request, 'nextseq_app/runandsamplesupdate.html', context)
        if run_form.has_changed() or sample_formset.has_changed():
            # dmpdir = settings.NEXTSEQAPP_DMPDIR
            # for fname in os.listdir(dmpdir):
            #    if os.path.isdir(os.path.join(dmpdir, fname)) and fname.endswith(runinfo.Flowcell_ID):
            #        basedirname = os.path.join(dmpdir, fname)
            # try:
            #    shutil.rmtree(os.path.join(basedirname, 'Data/Fastqs'))
            # except (FileNotFoundError, UnboundLocalError) as e:
            #    pass
            runinfo.jobstatus = 'ClickToSubmit'

        runinfo.save()
        sample_formset.save()

        return redirect('nextseq_app:rundetail', pk=runinfo.pk)

    return render(request, 'nextseq_app/runandsamplesupdate.html', {'run_form': run_form, 'sample_formset': sample_formset, 'runinfo': runinfo})


# @login

def SampleSheetCreateView(request, run_pk):
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
    deleterun = get_object_or_404(RunInfo, pk=run_pk)
    if deleterun.operator != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    deleterun.delete()
    return redirect('nextseq_app:userruns')


class UserRegisterView(FormView):
    form_class = UserRegisterForm
    template_name = 'nextseq_app/registration.html'
    success_url = reverse_lazy('nextseq_app:userruns')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        return HttpResponseRedirect(self.success_url)


class UserLoginView(View):
    form_class = UserLoginForm
    template_name = 'nextseq_app/login.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('nextseq_app:userruns')
            else:
                return render(request, self.template_name, {'form': form, 'error_message': 'Invalid login'})

        return render(request, self.template_name, {'form': form})


def logout_view(request):
    logout(request)
    return redirect('nextseq_app:userruns')


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, form.user)
            # messages.success(request, 'Your password was successfully updated!')
            return redirect('nextseq_app:userruns')
        # else:
            # messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'nextseq_app/change_password.html', {
        'form': form
    })


@transaction.atomic
def DemultiplexingView(request, run_pk):
    dmpdir = settings.NEXTSEQAPP_DMPDIR
    runinfo = get_object_or_404(RunInfo, pk=run_pk)
    if runinfo.operator != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    data = {}
    # print(runinfo.Flowcell_ID)
    for fname in os.listdir(dmpdir):
        # print(os.path.join(dmpdir,fname))
        if os.path.isdir(os.path.join(dmpdir, fname)) and fname.endswith(runinfo.Flowcell_ID):
            data['is_direxists'] = 1
            basedirname = os.path.join(dmpdir, fname)
            rundate = '20'+'-'.join([fname[i:i+2]
                                     for i in range(0, len(fname.split('_')[0]), 2)])
            # print(rundate)
            break
    # print(data)
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
                elif runinfo.experiment_type == 'TA':
                    i1_file = open(filename.replace('.csv', '_I1.csv'), 'w')
                    i1_file.write(','.join(["Lane", "Sample", "Index"])+'\n')

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
                            elif runinfo.experiment_type == 'TA':
                                i1_file.write(
                                    ','.join(['*', samples.Library_ID, i7seq])+'\n')
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
                ' ' + basedirname + ' ' + request.user.email
        elif runinfo.experiment_type == 'TA':
            cmd1 = './utility/runDemux10xATAC.sh ' + runinfo.Flowcell_ID + \
                ' ' + basedirname + ' ' + request.user.email
        else:
            cmd1 = './utility/runBcl2fastq.sh ' + runinfo.Flowcell_ID + \
                ' ' + basedirname + ' ' + request.user.email
        print(cmd1)

        p = subprocess.Popen(
            cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # thisjobid=p.pid

        data['writetosamplesheet'] = 1
        data['updatedate'] = '/'.join([rundate.split('-')[i]
                                       for i in [1, 2, 0]])
        return JsonResponse(data)

    else:
        return JsonResponse(data)


@transaction.atomic
def DemultiplexingView2(request, run_pk):
    dmpdir = settings.NEXTSEQAPP_DMPDIR
    runinfo = get_object_or_404(RunInfo, pk=run_pk)
    if runinfo.operator != request.user and not request.user.groups.filter(name='bioinformatics').exists():
        raise PermissionDenied
    data = {}
    # print(runinfo.Flowcell_ID)
    for fname in os.listdir(dmpdir):
        # print(os.path.join(dmpdir,fname))
        if os.path.isdir(os.path.join(dmpdir, fname)) and fname.endswith(runinfo.Flowcell_ID):
            data['is_direxists'] = 1
            basedirname = os.path.join(dmpdir, fname)
            rundate = '20'+'-'.join([fname[i:i+2]
                                     for i in range(0, len(fname.split('_')[0]), 2)])
            # print(rundate)
            break
    # print(data)
    if 'is_direxists' in data:
        # shutil.rmtree(os.path.join(basedirname, 'Data/Fastqs'))
        # os.mkdir(os.path.join(basedirname, 'Data/Fastqs'), exist_ok=True)

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
                elif runinfo.experiment_type == 'TA':
                    i1_file = open(filename.replace('.csv', '_I1.csv'), 'w')
                    i1_file.write(','.join(["Lane", "Sample", "Index"])+'\n')

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
                            elif runinfo.experiment_type == 'TA':
                                i1_file.write(
                                    ','.join(['*', samples.Library_ID, i7seq]) + '\n')

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
                elif runinfo.experiment_type == "TA":
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
                ' ' + basedirname + ' ' + request.user.email
        elif runinfo.experiment_type == 'TA':
            cmd1 = './utility/runDemux10xATAC.sh ' + runinfo.Flowcell_ID + \
                ' ' + basedirname + ' ' + request.user.email
        else:
            cmd1 = './utility/runBcl2fastq.sh ' + runinfo.Flowcell_ID + \
                ' ' + basedirname + ' ' + request.user.email
        print(cmd1)
        p = subprocess.Popen(
            cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # thisjobid=p.pid

        data['writetosamplesheet'] = 1
        data['updatedate'] = '/'.join([rundate.split('-')[i]
                                       for i in [1, 2, 0]])
        return JsonResponse(data)

    else:
        return JsonResponse(data)

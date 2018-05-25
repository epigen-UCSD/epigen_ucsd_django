from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm,UserLoginForm,RunCreationForm,SamplesInRunForm,SamplesToCreatForm
from django.views.generic import FormView, View
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from .models import Barcode, RunInfo, SamplesInRun
#from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.views.generic.edit import CreateView,UpdateView,DeleteView
import re,csv
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.forms import modelformset_factory
from django.forms import inlineformset_factory
# Create your views here.
# def index(request):
#     return HttpResponse("Hello, world!")
# class IndexView(TemplateView):
# 	template_name = "nextseq_app/index.html"
#@login_required
# class IndexView(ListView):
# 	template_name = "nextseq_app/index.html"
# 	context_object_name = 'RunInfo_list'
# 	def get_queryset(self):
# 		return RunInfo.objects.filter(operator=self.request.user)
barcodes_dic = {}
barcodes_list = Barcode.objects.all()
for barcodes in barcodes_list:
	barcodes_dic[barcodes.indexid] = barcodes.indexseq
#print(barcodes_dic)

def UniqueValidation(itemslist):
	if len(itemslist) != len(set(itemslist)):
		return False
	return True

def IndexValidation(i7list, i5list):
	duplicate = []

	combinelist = [x for x in list(zip(i7list,i5list)) if x[1]]
	#print(combinelist)
	for i in range(0, len(combinelist)):
		if combinelist[i] in combinelist[i+1:]:
			duplicate.append(combinelist[i])

	combinei7 = set([x[0] for x in list(zip(i7list,i5list)) if x[1]])
	#print(combinei7)
	singlei7 = [x[0] for x in list(zip(i7list,i5list)) if not x[1]]
	singlelist = list(combinei7) + singlei7
	#print(singlelist)
	for i in range(0, len(singlelist)):
		if singlelist[i] in singlelist[i+1:]:
			duplicate.append(singlelist[i])
	return duplicate



@login_required	
def IndexView(request):

	RunInfo_list = RunInfo.objects.filter(operator=request.user)
	return render(request, 'nextseq_app/index.html', {'RunInfo_list': RunInfo_list})

@method_decorator(login_required, name='dispatch')
class HomeView(ListView):
	template_name = "nextseq_app/home.html"
	context_object_name = 'RunInfo_list'

	def get_queryset(self):
		queryset_list = RunInfo.objects.all()
		if self.request.GET.get('q'):
			q = self.request.GET.get('q')
			#print(q)
			queryset_list = queryset_list.filter(
				Q(operator__username__icontains=q) | 
				Q(Flowcell__icontains=q) | 
				Q(read_type__icontains=q) | 
				Q(read_length__icontains=q)

				).distinct()

		return queryset_list

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['number'] = self.get_queryset().count()
		return context


@method_decorator(login_required, name='dispatch')
class RunDetailView(DetailView):
	model = RunInfo
	template_name = 'nextseq_app/detail.html'
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['barcode'] = barcodes_dic
		return context

@method_decorator(login_required, name='dispatch')
class RunDetailView2(DetailView):
	model = RunInfo
	template_name = 'nextseq_app/details.html'
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['barcode'] = barcodes_dic
		return context
# @login_required
# def RunDetailView(request, run_id):
# 	runinfo = get_object_or_404(RunInfo, pk=run_id)
# 	barcodei7 = {}
# 	barcodei5 = {}
# 	for samples in runinfo.samplesinrun_set.all():
# 		barcodequery = Barcode.objects.get(indexid=samples.i7index)
# 		barcodei7[samples] = barcodequery.indexseq
# 		samples
# 		print(samples)
# 		print(barcodei7[samples])
# 		barcodequery = Barcode.objects.get(indexid=samples.i5index)
# 		barcodei5[samples] = barcodequery.indexseq
# 	return render(request, 'nextseq_app/detail.html', {'runinfo': runinfo, 'barcodei7': barcodei7, 'barcodei5': barcodei5})
@method_decorator(login_required, name='dispatch')
class RunCreateView(CreateView):
	model = RunInfo
	fields = ['Flowcell','date','read_type','read_length']
	template_name = 'nextseq_app/createrun.html'
	#ields = '__all__'

@method_decorator(login_required, name='dispatch')
class RunCreateView2(CreateView):
	form_class = RunCreationForm
	template_name = 'nextseq_app/createrun.html'
	def form_valid(self, form):
		obj = form.save(commit=False)
		obj.operator = self.request.user
		return super().form_valid(form)

# @login_required
# def RunCreateView3(request):
# 	run_form = RunCreationForm(request.POST or None, prefix = "run")
# 	sample_form = SamplesInRunForm(request.POST or None, prefix = "samples")
# 	if run_form.is_valid() and sample_form.is_valid():
# 		runinfo = run_form.save(commit=False)
# 		runinfo.operator = request.user
# 		runinfo.save()
# 		sampleinfo = sample_form.save(commit=False)
# 		sampleinfo.singlerun = runinfo
# 		sampleinfo.save()
# 		return redirect('nextseq_app:rundetail',pk=runinfo.id)
# 	return render(request, 'nextseq_app/runandsamplesadd.html', {'run_form':run_form,'sample_form':sample_form})
	

@login_required
def RunCreateView3(request):
	run_form = RunCreationForm(request.POST or None, prefix = "run")
	formset = modelformset_factory(SamplesInRun, form=SamplesInRunForm,extra =3, can_order=True,  can_delete=True )
	sample_formset = formset(request.POST or None, queryset =  SamplesInRun.objects.none())

	if run_form.is_valid() and sample_formset.is_valid():
		runinfo = run_form.save(commit=False)
		runinfo.operator = request.user
		runinfo.save()
		instances = sample_formset.save(commit=False)
		for instance in instances:
			instance.singlerun = runinfo
			instance.save()
		return redirect('nextseq_app:rundetail',pk=runinfo.id)
	return render(request, 'nextseq_app/runandsamplesadd.html', {'run_form':run_form,'sample_formset':sample_formset})

@login_required
def RunCreateView4(request):
	run_form = RunCreationForm(request.POST or None)
	SamplesInlineFormSet = inlineformset_factory(RunInfo, SamplesInRun,fields = ['sampleid','i7index','i5index'],extra =2)
	sample_formset = SamplesInlineFormSet(instance=RunInfo())

	if run_form.is_valid():
		runinfo = run_form.save(commit=False)
		runinfo.operator = request.user
		sample_formset = SamplesInlineFormSet(request.POST,instance=runinfo)
		if sample_formset.is_valid():
			
			sampleid_list = []
			i7index_list = []
			i5index_list = []
			for form in sample_formset:
				try:
					sampleid_list.append(form.cleaned_data['sampleid'])
					i7index_list.append(form.cleaned_data['i7index'])
					i5index_list.append(form.cleaned_data['i5index'])
				except KeyError:
					pass
			#print(i7index_list)
			#print(i5index_list)
			duplicate = IndexValidation(i7index_list,i5index_list)
			if len(duplicate) > 0:
				context = {
				  'run_form':run_form,
				  'sample_formset':sample_formset,
				  'error_message': 'Duplicates:' + str(duplicate)

				}
				return render(request, 'nextseq_app/runandsamplesadd.html',context)


			runinfo.save()
			sample_formset.save()
			return redirect('nextseq_app:rundetail',pk=runinfo.id)
	
	return render(request, 'nextseq_app/runandsamplesadd.html', {'run_form':run_form,'sample_formset':sample_formset})

#creat run and samples or samples in bulk in one page
# @login_required
# def RunCreateView5(request):
# 	run_form = RunCreationForm(request.POST or None)
# 	SamplesInlineFormSet = inlineformset_factory(RunInfo, SamplesInRun,fields = ['sampleid','i7index','i5index'],extra =2)
# 	sample_formset = SamplesInlineFormSet(instance=RunInfo())
# 	form = SamplesToCreatForm(request.POST or None)

# 	if run_form.is_valid():
# 		runinfo = run_form.save(commit=False)
# 		runinfo.operator = request.user
# 		if 'singlsave' in request.POST:
# 			sample_formset = SamplesInlineFormSet(request.POST,instance=runinfo)
# 			if sample_formset.is_valid():
# 				runinfo.save()
# 				sample_formset.save()
# 				return redirect('nextseq_app:rundetail',pk=runinfo.id)
# 		elif 'bulksave' in request.POST and form.is_valid():
# 			runinfo.save()
# 			samplestocreat = form.cleaned_data['samplestocreat']
# 			tosave_list = []
# 			samplestocreat += '  \nsampleid'
# 			i7index_list = []
# 			i5index_list = []
# 			for samples in samplestocreat.split('\n'):
# 				samples_info = re.split(r'[\s\t]',samples)
# 				if samples_info[0] != 'sampleid':
# 					try:
# 						if samples_info[1] and samples_info[2]: 
# 							tosave_sample = SamplesInRun(
# 								singlerun=runinfo,
# 								sampleid=samples_info[0],
# 								i7index=Barcode.objects.get(indexid=samples_info[1]),
# 								i5index=Barcode.objects.get(indexid=samples_info[2]),
# 								)
# 						elif samples_info[1] and not samples_info[2]:
# 							tosave_sample = SamplesInRun(
# 								singlerun=runinfo,
# 								sampleid=samples_info[0],
# 								i7index=Barcode.objects.get(indexid=samples_info[1]),
# 								)
# 						elif not samples_info[1] and samples_info[2]:
# 							tosave_sample = SamplesInRun(
# 								singlerun=runinfo,
# 								sampleid=samples_info[0],
# 								i5index=Barcode.objects.get(indexid=samples_info[2]),
# 								)
# 						else:
# 							tosave_sample = SamplesInRun(
# 								singlerun=runinfo,
# 								sampleid=samples_info[0],
# 								)											

# 					except ObjectDoesNotExist:
# 						context = {
# 							'run_form':run_form,
# 							'sample_formset':sample_formset,
# 							'form':form,
# 							'error_message':'There are indexes that are not stored in the database!'
# 						}
# 						return render(request, 'nextseq_app/runandsamplesadd.html',context)


# 					tosave_list.append(tosave_sample)
# 			SamplesInRun.objects.bulk_create(tosave_list)
# 			return redirect('nextseq_app:rundetail',pk=runinfo.id)

# 	context={
# 		'run_form':run_form,
# 		'sample_formset':sample_formset,
# 		'form':form,
# 		}

# 	return render(request, 'nextseq_app/runandsamplesadd.html', context)


@login_required
def RunCreateView6(request):
	run_form = RunCreationForm(request.POST or None)
	form = SamplesToCreatForm(request.POST or None)

	if run_form.is_valid() and form.is_valid():
		runinfo = run_form.save(commit=False)
		runinfo.operator = request.user
		runinfo.save()
		samplestocreat = form.cleaned_data['samplestocreat']
		tosave_list = []
		samplestocreat += '   \nsampleid'
		i7index_list = []
		i5index_list = []
		for samples in samplestocreat.split('\n'):
			samples_info = re.split(r'[\s]',samples)
			#print(samples_info)
			if samples_info[0] != 'sampleid':
				try:
					if samples_info[1] and samples_info[2]: 
						tosave_sample = SamplesInRun(
							singlerun=runinfo,
							sampleid=samples_info[0],
							i7index=Barcode.objects.get(indexid=samples_info[1]),
							i5index=Barcode.objects.get(indexid=samples_info[2]),
							)
					elif samples_info[1] and not samples_info[2]:
						tosave_sample = SamplesInRun(
							singlerun=runinfo,
							sampleid=samples_info[0],
							i7index=Barcode.objects.get(indexid=samples_info[1]),
							)
					elif not samples_info[1] and samples_info[2]:
						tosave_sample = SamplesInRun(
							singlerun=runinfo,
							sampleid=samples_info[0],
							i5index=Barcode.objects.get(indexid=samples_info[2]),
							)
					else:
						tosave_sample = SamplesInRun(
							singlerun=runinfo,
							sampleid=samples_info[0],
							)												
					i7index_list.append(samples_info[1])
					i5index_list.append(samples_info[2])

				except ObjectDoesNotExist:
					context = {
							'run_form':run_form,
							'form':form,
							'error_message':'There are indexes that are not stored in the database!'
						}
					runinfo.delete()
					return render(request, 'nextseq_app/runandsamplesbulkadd.html',context)


				tosave_list.append(tosave_sample)
		duplicate = IndexValidation(i7index_list,i5index_list)
		if len(duplicate) > 0:
			runinfo.delete()
			context = {
				 'run_form':run_form,
				 'form':form,
				 'error_message': 'Duplicates:' + str(duplicate)

			}
			return render(request, 'nextseq_app/runandsamplesbulkadd.html',context)
		
		#runinfo.save()
		SamplesInRun.objects.bulk_create(tosave_list)

		return redirect('nextseq_app:rundetail',pk=runinfo.id)

	context={
		'run_form':run_form,
		'form':form,
		}

	return render(request, 'nextseq_app/runandsamplesbulkadd.html', context)

@login_required
def RunUpdateView2(request,run_pk):
	runinfo = get_object_or_404(RunInfo, pk=run_pk)
	run_form = RunCreationForm(request.POST or None, instance = runinfo)
	SamplesInlineFormSet = inlineformset_factory(RunInfo, SamplesInRun,fields = ['sampleid','i7index','i5index'],extra =3)
	sample_formset = SamplesInlineFormSet(request.POST or None, instance=runinfo)

	if run_form.is_valid() and sample_formset.is_valid():
		runinfo = run_form.save(commit=False)
		runinfo.operator = request.user

		sampleid_list = []
		i7index_list = []
		i5index_list = []
		for form in sample_formset:
			try:
				sampleid_list.append(form.cleaned_data['sampleid'])
				i7index_list.append(form.cleaned_data['i7index'])
				i5index_list.append(form.cleaned_data['i5index'])
			except KeyError:
				pass

		duplicate = IndexValidation(i7index_list,i5index_list)
		if len(duplicate) > 0:
			context = {
				 'run_form':run_form,
				 'sample_formset':sample_formset,
				 'error_message': 'Duplicates:' + str(duplicate)

			}
			return render(request, 'nextseq_app/runandsamplesupdate.html',context)
			
		runinfo.save()
		sample_formset.save()
		return redirect('nextseq_app:rundetail',pk=runinfo.pk)
		
	return render(request, 'nextseq_app/runandsamplesupdate.html', {'run_form':run_form,'sample_formset':sample_formset})

	


@login_required
def SampleCreateView(request, run_pk):
	#form = SamplesInRunForm(request.POST or None, request.FILES or None)
	form = SamplesInRunForm(request.POST or None)
	runinfo = get_object_or_404(RunInfo, pk=run_pk)
	if form.is_valid():
		runinfo_samples = runinfo.samplesinrun_set.all()
		for s in runinfo_samples:
			if s.sampleid == form.cleaned_data.get("sampleid"):
				context ={
					'form':form,
					'runinfo':runinfo,
					'error_message':'You already added that sample',
				}
				return render(request, 'nextseq_app/createsamples.html', context)
		obj = form.save(commit=False)
		obj.singlerun = runinfo
		obj.save()
		return redirect('nextseq_app:rundetail',pk=runinfo.id)
	return render(request, 'nextseq_app/createsamples.html', {'form':form,'runinfo':runinfo})

@login_required
def SamplesDeleteView(request, run_pk):
	delete_list = request.GET.getlist('delete_list')
	if request.method == "POST":
		SamplesInRun.objects.filter(singlerun=RunInfo.objects.get(pk=run_pk),sampleid__in=delete_list).delete()
		return redirect('nextseq_app:rundetail',pk=run_pk)
	return render(request, 'nextseq_app/samples_confirm_delete.html', {'delete_list':delete_list,'run_pk':run_pk})

@login_required
def SamplesBulkCreateView(request,run_pk):
	runinfo = get_object_or_404(RunInfo, pk=run_pk)
	if request.method == 'POST':
		form = SamplesToCreatForm(request.POST)
		#print(form)
		if form.is_valid():
			samplestocreat = form.cleaned_data['samplestocreat']
			tosave_list = []
			samplestocreat += '  \nsampleid'
			#print(samplestocreat)
			for samples in samplestocreat.split('\n'):
				#print(samples)
				samples_info = re.split(r'[\s]',samples)
				#print(samples_info)
				if samples_info[0] != 'sampleid':
					try:
						if samples_info[1] and samples_info[2]: 
							tosave_sample = SamplesInRun(
								singlerun=runinfo,
								sampleid=samples_info[0],
								i7index=Barcode.objects.get(indexid=samples_info[1]),
								i5index=Barcode.objects.get(indexid=samples_info[2]),
								)
						elif samples_info[1] and not samples_info[2]:
							tosave_sample = SamplesInRun(
								singlerun=runinfo,
								sampleid=samples_info[0],
								i7index=Barcode.objects.get(indexid=samples_info[1]),
								)
						elif not samples_info[1] and samples_info[2]:
							tosave_sample = SamplesInRun(
								singlerun=runinfo,
								sampleid=samples_info[0],
								i5index=Barcode.objects.get(indexid=samples_info[2]),
								)
						else:
							tosave_sample = SamplesInRun(
								singlerun=runinfo,
								sampleid=samples_info[0],
								)												

					except ObjectDoesNotExist:
						context = {
							'form':form,
							'error_message':'There are indexes that are not stored in the database!'
						}
						return render(request, 'nextseq_app/createsamples_inbulk.html',context)


					tosave_list.append(tosave_sample)
			SamplesInRun.objects.bulk_create(tosave_list)
			return redirect('nextseq_app:rundetail',pk=run_pk)

	else:
		form = SamplesToCreatForm()
	return render(request, 'nextseq_app/createsamples_inbulk.html',{'form':form,'runinfo':runinfo})

@login_required
def SampleSheetCreateView(request,run_pk):
	runinfo = get_object_or_404(RunInfo, pk=run_pk)
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="SampleSheet.csv"'
	writer = csv.writer(response)
	writer.writerow(['[Header]'])
	writer.writerow(['IEMFileVersion','5'])
	writer.writerow(['Date',runinfo.date])
	writer.writerow(['Workflow','GenerateFASTQ'])
	writer.writerow(['Application','NextSeq FASTQ Only'])
	writer.writerow(['Instrument Type','NextSeq/MiniSeq'])
	writer.writerow(['Assay','Nextera XT / TruSeq LT'])
	writer.writerow(['Index Adapters','Nextera XT v2 Index Kit / TruSeq LT'])
	writer.writerow(['Description'])
	writer.writerow(['Chemistry','Amplicon'])
	writer.writerow([''])
	writer.writerow(['[Reads]'])
	if runinfo.read_type == 'PE':
		a = runinfo.read_length
		writer.writerow([a])
		writer.writerow([a])
	else:
		a = runinfo.read_length
		writer.writerow([a])
	writer.writerow([''])
	writer.writerow(['[Settings]'])
	writer.writerow([''])
	writer.writerow(['Sample_ID','Sample_Name','Sample_Plate','Sample_Well','I7_Index_ID','index','I5_Index_ID','index2','Sample_Project','Description'])
	samples_list = runinfo.samplesinrun_set.all()
	for samples in samples_list:
		i7id = samples.i7index or ''
		i5id = samples.i5index or ''
		i7seq= Barcode.objects.get(indexid=i7id).indexseq if i7id!='' else ''
		i5seq= Barcode.objects.get(indexid=i5id).indexseq if i5id!='' else ''
		writer.writerow([samples.sampleid,'','','',i7id,i7seq,i5id,i5seq,'',''])									
	return response



@method_decorator(login_required, name='dispatch')
class RunUpdateView(UpdateView):
	model = RunInfo
	fields = ['Flowcell','date','read_type','read_length']
	template_name = 'nextseq_app/updaterun.html'

@method_decorator(login_required, name='dispatch')
class RunDeleteView(DeleteView):
	model = RunInfo
	success_url = reverse_lazy('nextseq_app:index')


class UserRegisterView(FormView):
	form_class = UserRegisterForm
	template_name = 'nextseq_app/registration.html'
	success_url = reverse_lazy('nextseq_app:index')

	def form_valid(self, form):
		user = form.save(commit=False)
		user.set_password(form.cleaned_data['password1'])
		user.save()
		return HttpResponseRedirect(self.success_url)

@method_decorator(never_cache, name='dispatch')
class UserLoginView(View):
	form_class = UserLoginForm
	template_name = 'nextseq_app/login.html'

	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name,{'form':form})

	def post(self, request):
		form = self.form_class(request.POST)

		if form.is_valid():
			user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
			if user is not None:
				if user.is_active:
					login(request, user)
					return redirect('nextseq_app:home')
			else:
				return render(request, self.template_name,{'form':form,'error_message':'Invalid login'})

		return render(request, self.template_name,{'form':form})


def logout_view(request):
	logout(request)
	return redirect('nextseq_app:index')












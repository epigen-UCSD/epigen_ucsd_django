from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,Http404
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm,UserLoginForm,RunCreationForm,LibrariesInRunForm,SamplesToCreatForm
from django.views.generic import FormView, View
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from .models import Barcode, RunInfo, LibrariesInRun
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.views.generic.edit import CreateView,UpdateView,DeleteView
import re,csv
from django.core.exceptions import ObjectDoesNotExist,PermissionDenied
from django.db.models import Q
from django.db import transaction
from django.forms import modelformset_factory,inlineformset_factory
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

def BarcodeDic():
	barcodes_dic = {}
	barcodes_list = Barcode.objects.all()
	for barcodes in barcodes_list:
		barcodes_dic[barcodes.indexid] = barcodes.indexseq
	return barcodes_dic


def UniqueValidation(tosavelist,existinglist):
	return list(set(tosavelist).intersection(set(existinglist)))

def SelfUniqueValidation(tosavelist):
	duplicate = []
	for i in range(0, len(tosavelist)):
		if tosavelist[i] in tosavelist[i+1:]:
			duplicate.append(tosavelist[i])
	return duplicate

def IndexValidation(i7list, i5list):
	duplicate = []

	combinelist = [x for x in list(zip(i7list,i5list)) if x[1]]
	#print(combinelist)
	for i in range(0, len(combinelist)):
		if combinelist[i] in combinelist[i+1:]:
			duplicate.append(combinelist[i])

	combinei7 = set([x[0] for x in list(zip(i7list,i5list)) if x[1]])
	#print(combinei7)
	singlei7 = [x[0] for x in list(zip(i7list,i5list)) if not x[1] and x[0]]
	print(singlei7)
	singlelist = list(combinei7) + singlei7
	#print(singlelist)
	for i in range(0, len(singlelist)):
		if singlelist[i] in singlelist[i+1:]:
			duplicate.append(singlelist[i])
	return duplicate



@login_required	
def IndexView(request):

	RunInfo_list = RunInfo.objects.filter(operator=request.user)
	return render(request, 'nextseq_app/userrunsinfo.html', {'RunInfo_list': RunInfo_list})

@method_decorator(login_required, name='dispatch')
class HomeView(ListView):
	template_name = "nextseq_app/runsinfo.html"
	context_object_name = 'RunInfo_list'

	def get_queryset(self):
		queryset_list = RunInfo.objects.all()
		if self.request.GET.get('q'):
			q = self.request.GET.get('q')
			#print(q)
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

@login_required	
def AllSamplesView(request):
	Samples_list = LibrariesInRun.objects.all()
	barcodes_dic = BarcodeDic()
	number = LibrariesInRun.objects.count()

	context = {
		'Samples_list': Samples_list,
		'barcode': barcodes_dic,
		'number' : number

	}
	return render(request, 'nextseq_app/samplesinfo.html', context)

@login_required	
def UserSamplesView(request):
	userruns = RunInfo.objects.filter(operator=request.user)
	Samples_list = LibrariesInRun.objects.filter(singlerun__in=userruns)
	barcodes_dic = BarcodeDic()
	number = Samples_list.count()
	usersamples = True

	context = {
		'Samples_list': Samples_list,
		'barcode': barcodes_dic,
		'number' : number,
		'usersamples': usersamples
	}
	return render(request, 'nextseq_app/usersamplesinfo.html', context)


# @method_decorator(login_required, name='dispatch')
# class RunDetailView(DetailView):
# 	model = RunInfo
# 	template_name = 'nextseq_app/detail.html'
# 	def get_context_data(self, **kwargs):
# 		context = super().get_context_data(**kwargs)
# 		context['barcode'] = barcodes_dic
# 		return context

@method_decorator(login_required, name='dispatch')
class RunDetailView2(DetailView):
	model = RunInfo
	template_name = 'nextseq_app/details.html'
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		#context['barcode'] = barcodes_dic
		context['barcode'] = BarcodeDic()
		return context

@method_decorator(login_required, name='dispatch')
class RunDetailViewhome(DetailView):
	model = RunInfo
	template_name = 'nextseq_app/homedetails.html'
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		#context['barcode'] = barcodes_dic
		context['barcode'] = BarcodeDic()
		return context

# @method_decorator(login_required, name='dispatch')
# class RunCreateView(CreateView):
# 	model = RunInfo
# 	fields = ['Flowcell_ID','date','read_type','read_length']
# 	template_name = 'nextseq_app/createrun.html'


# @method_decorator(login_required, name='dispatch')
# class RunCreateView2(CreateView):
# 	form_class = RunCreationForm
# 	template_name = 'nextseq_app/createrun.html'
# 	def form_valid(self, form):
# 		obj = form.save(commit=False)
# 		obj.operator = self.request.user
# 		return super().form_valid(form)

	

# @login_required
# def RunCreateView3(request):
# 	run_form = RunCreationForm(request.POST or None, prefix = "run")
# 	formset = modelformset_factory(LibrariesInRun, form=LibrariesInRunForm,extra =3, can_order=True,  can_delete=True )
# 	sample_formset = formset(request.POST or None, queryset =  LibrariesInRun.objects.none())

# 	if run_form.is_valid() and sample_formset.is_valid():
# 		runinfo = run_form.save(commit=False)
# 		runinfo.operator = request.user
# 		runinfo.save()
# 		instances = sample_formset.save(commit=False)
# 		for instance in instances:
# 			instance.singlerun = runinfo
# 			instance.save()
# 		return redirect('nextseq_app:rundetail',pk=runinfo.id)
# 	return render(request, 'nextseq_app/runandsamplesadd.html', {'run_form':run_form,'sample_formset':sample_formset})

@login_required
@transaction.atomic
def RunCreateView4(request):
	run_form = RunCreationForm(request.POST or None)
	SamplesInlineFormSet = inlineformset_factory(RunInfo, LibrariesInRun,fields = ['Library_ID','i7index','i5index'],extra =2)
	sample_formset = SamplesInlineFormSet(request.POST or None, instance=RunInfo())

	if run_form.is_valid():
		runinfo = run_form.save(commit=False)
		runinfo.operator = request.user
		sample_formset = SamplesInlineFormSet(request.POST,instance=runinfo)
		if sample_formset.is_valid():
			sample_formset.save(commit=False)
			Library_ID_list = []
			i7index_list = []
			i5index_list = []
			for form in sample_formset:
				if form not in sample_formset.deleted_forms:
					#print(form.as_table())
					try:
						Library_ID_list.append(form.cleaned_data['Library_ID'])
						i7index_list.append(form.cleaned_data['i7index'])
						i5index_list.append(form.cleaned_data['i5index'])
					except KeyError:
						pass			

			duplicate = IndexValidation(i7index_list,i5index_list)
			if len(duplicate) > 0:
				context = {
				  'run_form':run_form,
				  'sample_formset':sample_formset,
				  'error_message': 'Duplicates:\t' + str(duplicate)

				}
				return render(request, 'nextseq_app/runandsamplesadd.html',context)


			runinfo.save()
			sample_formset.save()
			return redirect('nextseq_app:rundetail',pk=runinfo.id)
	
	return render(request, 'nextseq_app/runandsamplesadd.html', {'run_form':run_form,'sample_formset':sample_formset})



@login_required
@transaction.atomic
def RunCreateView6(request):
	run_form = RunCreationForm(request.POST or None)
	form = SamplesToCreatForm(request.POST or None)

	if run_form.is_valid() and form.is_valid():
		runinfo = run_form.save(commit=False)
		runinfo.operator = request.user
		
		samplestocreat = form.cleaned_data['samplestocreat']
		tosave_list = []
		samplestocreat += '   \nLibrary_ID'
		i7index_list = []
		i5index_list = []
		libraryid_list = []
		for samples in samplestocreat.split('\n'):
			samples_info = re.split(r'[\s]',samples)
			#print(samples_info)
			if samples_info[0] != 'Library_ID':
				try:
					if samples_info[1] and samples_info[2]: 
						tosave_sample = LibrariesInRun(

							Library_ID=samples_info[0],
							i7index=Barcode.objects.get(indexid=samples_info[1]),
							i5index=Barcode.objects.get(indexid=samples_info[2]),
							)
					elif samples_info[1] and not samples_info[2]:
						tosave_sample = LibrariesInRun(

							Library_ID=samples_info[0],
							i7index=Barcode.objects.get(indexid=samples_info[1]),
							)
					elif not samples_info[1] and samples_info[2]:
						tosave_sample = LibrariesInRun(

							Library_ID=samples_info[0],
							i5index=Barcode.objects.get(indexid=samples_info[2]),
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
							'run_form':run_form,
							'form':form,
							'error_message':'There are indexes that are not stored in the database for this library: '+'\t'.join(samples_info)
						}

					return render(request, 'nextseq_app/runandsamplesbulkadd.html',context)


				tosave_list.append(tosave_sample)
		libraryselfduplicate = SelfUniqueValidation(libraryid_list)
		if len(libraryselfduplicate) > 0:

			context = {
				 'run_form':run_form,
				 'form':form,
				 'error_message': 'Duplicate Library within this run:\t' + ';\t'.join(list(libraryselfduplicate))

			}
			return render(request, 'nextseq_app/runandsamplesbulkadd.html',context)

		existinglibray = list(LibrariesInRun.objects.values_list('Library_ID',flat=True))
		libraynotuniq = UniqueValidation(libraryid_list,existinglibray)

		if len(libraynotuniq) > 0:

			context = {
				 'run_form':run_form,
				 'form':form,
				 'error_message': 'Libraries already exit:\t' + ';\t'.join(list(libraynotuniq))

			}
			return render(request, 'nextseq_app/runandsamplesbulkadd.html',context)

		duplicate = IndexValidation(i7index_list,i5index_list)
		if len(duplicate) > 0:

			context = {
				 'run_form':run_form,
				 'form':form,
				 'error_message': 'Duplicates:\t' + str(duplicate)

			}
			return render(request, 'nextseq_app/runandsamplesbulkadd.html',context)
		
		runinfo.save()
		for samples in tosave_list:
			 samples.singlerun=runinfo
		LibrariesInRun.objects.bulk_create(tosave_list)

		return redirect('nextseq_app:rundetail',pk=runinfo.id)

	context={
		'run_form':run_form,
		'form':form,
		}

	return render(request, 'nextseq_app/runandsamplesbulkadd.html', context)

@login_required
@transaction.atomic
def RunUpdateView2(request,username,run_pk):
	runinfo = get_object_or_404(RunInfo, pk=run_pk)
	if runinfo.operator != request.user:
		raise PermissionDenied
	run_form = RunCreationForm(request.POST or None, instance = runinfo)
	SamplesInlineFormSet = inlineformset_factory(RunInfo, LibrariesInRun,fields = ['Library_ID','i7index','i5index'],extra =3)
	sample_formset = SamplesInlineFormSet(request.POST or None, instance=runinfo)

	if run_form.is_valid() and sample_formset.is_valid():
		runinfo = run_form.save(commit=False)
		runinfo.operator = request.user

		Library_ID_list = []
		i7index_list = []
		i5index_list = []
		for form in sample_formset:
			try:
				Library_ID_list.append(form.cleaned_data['Library_ID'])
				i7index_list.append(form.cleaned_data['i7index'])
				i5index_list.append(form.cleaned_data['i5index'])
			except KeyError:
				pass

		duplicate = IndexValidation(i7index_list,i5index_list)
		if len(duplicate) > 0:
			context = {
				 'run_form':run_form,
				 'sample_formset':sample_formset,
				 'error_message': 'Duplicates:\t' + str(duplicate),
				 'runinfo': runinfo,

			}
			return render(request, 'nextseq_app/runandsamplesupdate.html',context)
			
		runinfo.save()
		sample_formset.save()
		return redirect('nextseq_app:rundetail',pk=runinfo.pk)
		
	return render(request, 'nextseq_app/runandsamplesupdate.html', {'run_form':run_form,'sample_formset':sample_formset,'runinfo': runinfo})

	


# @login_required
# def SampleCreateView(request, run_pk):
# 	#form = LibrariesInRunForm(request.POST or None, request.FILES or None)
# 	form = LibrariesInRunForm(request.POST or None)
# 	runinfo = get_object_or_404(RunInfo, pk=run_pk)
# 	if form.is_valid():
# 		runinfo_samples = runinfo.LibrariesInRun_set.all()
# 		for s in runinfo_samples:
# 			if s.Library_ID == form.cleaned_data.get("Library_ID"):
# 				context ={
# 					'form':form,
# 					'runinfo':runinfo,
# 					'error_message':'You already added that sample',
# 				}
# 				return render(request, 'nextseq_app/createsamples.html', context)
# 		obj = form.save(commit=False)
# 		obj.singlerun = runinfo
# 		obj.save()
# 		return redirect('nextseq_app:rundetail',pk=runinfo.id)
# 	return render(request, 'nextseq_app/createsamples.html', {'form':form,'runinfo':runinfo})

# @login_required
# def SamplesDeleteView(request, run_pk):
# 	delete_list = request.GET.getlist('delete_list')
# 	if request.method == "POST":
# 		LibrariesInRun.objects.filter(singlerun=RunInfo.objects.get(pk=run_pk),Library_ID__in=delete_list).delete()
# 		return redirect('nextseq_app:rundetail',pk=run_pk)
# 	return render(request, 'nextseq_app/samples_confirm_delete.html', {'delete_list':delete_list,'run_pk':run_pk})

# @login_required
# def SamplesBulkCreateView(request,run_pk):
# 	runinfo = get_object_or_404(RunInfo, pk=run_pk)
# 	if request.method == 'POST':
# 		form = SamplesToCreatForm(request.POST)
# 		#print(form)
# 		if form.is_valid():
# 			samplestocreat = form.cleaned_data['samplestocreat']
# 			tosave_list = []
# 			samplestocreat += '  \nLibrary_ID'
# 			#print(samplestocreat)
# 			for samples in samplestocreat.split('\n'):
# 				#print(samples)
# 				samples_info = re.split(r'[\s]',samples)
# 				#print(samples_info)
# 				if samples_info[0] != 'Library_ID':
# 					try:
# 						if samples_info[1] and samples_info[2]: 
# 							tosave_sample = LibrariesInRun(
# 								singlerun=runinfo,
# 								Library_ID=samples_info[0],
# 								i7index=Barcode.objects.get(indexid=samples_info[1]),
# 								i5index=Barcode.objects.get(indexid=samples_info[2]),
# 								)
# 						elif samples_info[1] and not samples_info[2]:
# 							tosave_sample = LibrariesInRun(
# 								singlerun=runinfo,
# 								Library_ID=samples_info[0],
# 								i7index=Barcode.objects.get(indexid=samples_info[1]),
# 								)
# 						elif not samples_info[1] and samples_info[2]:
# 							tosave_sample = LibrariesInRun(
# 								singlerun=runinfo,
# 								Library_ID=samples_info[0],
# 								i5index=Barcode.objects.get(indexid=samples_info[2]),
# 								)
# 						else:
# 							tosave_sample = LibrariesInRun(
# 								singlerun=runinfo,
# 								Library_ID=samples_info[0],
# 								)												

# 					except ObjectDoesNotExist:
# 						context = {
# 							'form':form,
# 							'error_message':'There are indexes that are not stored in the database!'
# 						}
# 						return render(request, 'nextseq_app/createsamples_inbulk.html',context)


# 					tosave_list.append(tosave_sample)
# 			LibrariesInRun.objects.bulk_create(tosave_list)
# 			return redirect('nextseq_app:rundetail',pk=run_pk)

# 	else:
# 		form = SamplesToCreatForm()
# 	return render(request, 'nextseq_app/createsamples_inbulk.html',{'form':form,'runinfo':runinfo})

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
	samples_list = runinfo.librariesinrun_set.all()
	for samples in samples_list:
		i7id = samples.i7index or ''
		i5id = samples.i5index or ''
		i7seq= Barcode.objects.get(indexid=i7id).indexseq if i7id!='' else ''
		i5seq= Barcode.objects.get(indexid=i5id).indexseq if i5id!='' else ''
		writer.writerow([samples.Library_ID,'','','',i7id,i7seq,i5id,i5seq,'',''])									
	return response



# @method_decorator(login_required, name='dispatch')
# class RunUpdateView(UpdateView):
# 	model = RunInfo
# 	fields = ['Flowcell_ID','date','read_type','read_length']
# 	template_name = 'nextseq_app/updaterun.html'

# @method_decorator(login_required, name='dispatch')
# class RunDeleteView(DeleteView):
# 	model = RunInfo
# 	success_url = reverse_lazy('nextseq_app:userruns')

@login_required
def RunDeleteView2(request,run_pk):
	deleterun = get_object_or_404(RunInfo, pk=run_pk)
	if deleterun.operator != request.user:
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
					return redirect('nextseq_app:userruns')
			else:
				return render(request, self.template_name,{'form':form,'error_message':'Invalid login'})

		return render(request, self.template_name,{'form':form})


def logout_view(request):
	logout(request)
	return redirect('nextseq_app:userruns')


@login_required
def change_password(request):
	if request.method == 'POST':
		form = PasswordChangeForm(user=request.user, data=request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, form.user)
			#messages.success(request, 'Your password was successfully updated!')
			return redirect('nextseq_app:userruns')
		#else:
			#messages.error(request, 'Please correct the error below.')
	else:
		form = PasswordChangeForm(user=request.user)
	return render(request, 'nextseq_app/change_password.html', {
		'form': form
	})








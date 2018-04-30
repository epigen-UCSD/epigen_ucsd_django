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

@login_required	
def IndexView(request):

	RunInfo_list = RunInfo.objects.filter(operator=request.user)
	return render(request, 'nextseq_app/index.html', {'RunInfo_list': RunInfo_list})

@method_decorator(login_required, name='dispatch')
class RunDetailView(DetailView):
	model = RunInfo
	template_name = 'nextseq_app/detail.html'
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
	fields = ['runid','date','is_pe','reads_length']
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

@login_required
def SampleCreateView(request, run_pk):
	form = SamplesInRunForm(request.POST or None, request.FILES or None)
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
		if form.is_valid():
			samplestocreat = form.cleaned_data['samplestocreat']
			tosave_list = []
			for samples in samplestocreat.split('\n'):
				samples_info = re.split(r'[\s\t]',samples.strip('\r'))
				if samples_info[0] != 'sampleid':
					try:
						tosave_sample = SamplesInRun(
							singlerun=runinfo,
							sampleid=samples_info[0],
							i7index=Barcode.objects.get(indexid=samples_info[1]),
							i5index=Barcode.objects.get(indexid=samples_info[2]),
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
	if runinfo.is_pe:
		a = runinfo.reads_length
		writer.writerow([a])
		writer.writerow([a])
	writer.writerow([''])
	writer.writerow(['[Settings]'])
	writer.writerow([''])
	writer.writerow(['Sample_ID','Sample_Name','Sample_Plate','Sample_Well','I7_Index_ID','index','I5_Index_ID','index2','Sample_Project','Description'])
	samples_list = runinfo.samplesinrun_set.all()
	for samples in samples_list:
		i7id = samples.i7index
		i5id = samples.i5index
		i7seq= Barcode.objects.get(indexid=i7id).indexseq
		i5seq= Barcode.objects.get(indexid=i5id).indexseq
		writer.writerow([samples.sampleid,'','','',i7id,i7seq,i5id,i5seq,'',''])									
	return response



@method_decorator(login_required, name='dispatch')
class RunUpdateView(UpdateView):
	model = RunInfo
	fields = ['runid','date','is_pe','reads_length']
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
					return redirect('nextseq_app:index')
			else:
				return render(request, self.template_name,{'form':form,'error_message':'Invalid login'})

		return render(request, self.template_name,{'form':form})


def logout_view(request):
	logout(request)
	return redirect('nextseq_app:index')












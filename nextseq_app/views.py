from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm,UserLoginForm,RunCreationForm
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












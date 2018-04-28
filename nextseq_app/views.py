from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegisterForm,UserLoginForm
from django.views.generic import FormView, View
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView


# Create your views here.
# def index(request):
#     return HttpResponse("Hello, world!")
class IndexView(TemplateView):
	template_name = "nextseq_app/index.html"


class UserRegisterView(FormView):
	form_class = UserRegisterForm
	template_name = 'nextseq_app/registration.html'
	success_url = reverse_lazy('nextseq_app:index')

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












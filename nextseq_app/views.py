from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import UserForm
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

# Create your views here.
def index(request):
    return HttpResponse("Hello, world!")

class UserRegisterView(FormView):
	form_class = UserForm
	template_name = 'nextseq_app/registration.html'
	success_url = reverse_lazy('nextseq_app:index')

	def form_valid(self, form):
		user = form.save(commit=False)
		user.set_password(form.cleaned_data['password1'])
		user.save()
		return HttpResponseRedirect(self.success_url)


from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import UserForm
from django.views.generic import View

# Create your views here.
def index(request):
    return HttpResponse("Hello, world!")

class UserFormView(View):
	form_class = UserForm
	template_name = 'nextseq_app/registration.html'

	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name,{'form':form})

	def post(self, request):
		form = self.form_class(request.POST)

		if form.is_valid():
			user = form.save(commit=False)
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user.set_password(password)
			user.save()

			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					return redirect('nextseq_app:index')
		return render(request, self.template_name,{'form':form})

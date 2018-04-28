from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils.translation import gettext_lazy as _

class UserForm(UserCreationForm):
	#password = forms.CharField(widget=forms.PasswordInput)
	class Meta:
		model = User
		fields = ['username','email']
		#help_texts = {'username': '',}

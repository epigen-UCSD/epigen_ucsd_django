from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
#from django.utils.translation import gettext_lazy as _
from .models import RunInfo
from django.forms import ModelForm


class UserRegisterForm(UserCreationForm):

	class Meta:
		model = User
		fields = ['username','email']
		#help_texts = {'username': '',}
class UserLoginForm(forms.Form):

	username = forms.CharField()
	password = forms.CharField(widget=forms.PasswordInput)

class RunCreationForm(ModelForm):

	class Meta:
		model = RunInfo
		fields = ['runid','date','is_pe','reads_length']
		widgets ={
			 'date': forms.DateInput(),

		}

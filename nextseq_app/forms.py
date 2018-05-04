from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
#from django.utils.translation import gettext_lazy as _
from .models import RunInfo,SamplesInRun
from django.forms import ModelForm


class UserRegisterForm(UserCreationForm):

	class Meta:
		model = User
		fields = ['username','email']
		help_texts = {
		'username': '',
		'password1':'',
		'password2':''
		}
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
class SamplesInRunForm(ModelForm):

	class Meta:
		model = SamplesInRun
		fields = ['sampleid','i7index','i5index']

class SamplesToCreatForm(forms.Form):
	samplestocreat = forms.CharField(
			label='Samples to Save:',
			widget=forms.Textarea(attrs={'cols': 40, 'rows': 20}),
			initial='sampleid i7index i5index(seperated by Space or Tab)\n'
		)
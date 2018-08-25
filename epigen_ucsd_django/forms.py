from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms


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
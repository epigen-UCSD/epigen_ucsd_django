from django import forms
from django.contrib.auth.models import User,Group
from epigen_ucsd_django.models import CollaboratorPersonInfo,Person_Index,Group_Institution
import secrets
import string

class UserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('username','first_name','last_name','password')
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		alphabet = string.ascii_letters + string.digits
		passwordrand = ''.join(secrets.choice(alphabet) for i in range(10))
		self.initial['password'] = passwordrand
class CollaboratorPersonForm(forms.ModelForm):
	class Meta:
		model = CollaboratorPersonInfo
		fields = ('email','phone','index')

class GroupForm(forms.Form):
	name = forms.CharField(\
		label='Group Name',
		widget = forms.TextInput({'class': 'ajax_groupinput_form', 'size': 30}),
		)
	# def __init__(self, *args, **kwargs):
	# 	super().__init__(*args, **kwargs)
	# 	self.fields['name'].label = "Group name"
	def clean_name(self):
		data = self.cleaned_data['name']
		if not Group.objects.filter(name=data).exists() :
			raise forms.ValidationError('Invalid Group Name!')
		else:
			return data
class GroupCreateForm(forms.ModelForm):
	class Meta:
		model = Group
		fields = ('name',)

class GroupInstitutionCreateForm(forms.ModelForm):
	class Meta:
		model = Group_Institution
		fields = ('institution',)

class PersonIndexForm(forms.ModelForm):
	class Meta:
		model = Person_Index
		fields = ('index_name',)
		help_texts = {
		'index_name': 'If the Collaborator(fiscal contact person)you are adding is in charge of the index that we\
		 will charge on,please fill in',
		}
class PersonIndexCreateForm(forms.ModelForm):
	person = forms.ModelChoiceField(queryset=CollaboratorPersonInfo.objects.all(),\
		widget=forms.TextInput({'class': 'ajax_collabinput_form', 'size': 50}), required=False)
	class Meta:
		model = Person_Index
		fields = ('index_name','person')

class CollabInfoAddForm(forms.ModelForm):
	person_id = forms.ModelChoiceField(queryset=User.objects.all(),\
		widget=forms.TextInput({'class': 'ajax_collabinput_form', 'size': 50}), required=False)
	class Meta:
		model = CollaboratorPersonInfo
		fields = ('person_id','email','phone','index')


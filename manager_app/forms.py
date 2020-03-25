from django import forms
from django.contrib.auth.models import User,Group
from epigen_ucsd_django.models import CollaboratorPersonInfo,Group_Institution
import secrets
import string
from collaborator_app.models import ServiceInfo,ServiceRequest,ServiceRequestItem
from django.db.models import Prefetch

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

class ContactForm(forms.Form):
	group =forms.CharField(\
		label='Group Name',
		widget = forms.TextInput({'class': 'ajax_groupinput_form', 'size': 30}),
		)
	research_contact = forms.ModelChoiceField(queryset=CollaboratorPersonInfo.objects.all(),required=False)
	research_contact_email = forms.ChoiceField(required=False)
	# def __init__(self, *args, **kwargs):
	# 	super().__init__(*args, **kwargs)
	# 	self.fields['name'].label = "Group name"
	def clean_group(self):
		data = self.cleaned_data['group']
		if not Group.objects.filter(name=data).exists() :
			raise forms.ValidationError('Invalid Group Name!')
		else:
			return data
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['research_contact'].queryset = CollaboratorPersonInfo.objects.none()
		if 'group' in self.data:
			gname = self.data.get('group')
			print(gname)
			self.fields['research_contact'].queryset = CollaboratorPersonInfo.objects.\
			filter(person_id__groups__name__in=[gname]).\
			prefetch_related(Prefetch('person_id__groups'))
			self.fields['research_contact'].label_from_instance = \
			lambda obj: "%s %s" % (obj.person_id.first_name, \
			obj.person_id.last_name)
			if 'research_contact' in self.data:
				research_contact = self.data.get('research_contact')
				self.fields['research_contact_email'] = forms.ChoiceField(choices=[(email,email) for email in CollaboratorPersonInfo.objects.get(id=research_contact).email],required=False)


class GroupCreateForm(forms.ModelForm):
	class Meta:
		model = Group
		fields = ('name',)

class GroupInstitutionCreateForm(forms.ModelForm):
	class Meta:
		model = Group_Institution
		fields = ('institution',)

class CollabInfoAddForm(forms.ModelForm):
	person_id = forms.ModelChoiceField(queryset=User.objects.all(),\
		widget=forms.TextInput({'class': 'ajax_collabinput_form', 'size': 50}))
	class Meta:
		model = CollaboratorPersonInfo
		fields = ('person_id','email','phone','index')

class ServiceRequestItemCreationForm(forms.ModelForm):
	class Meta:
		model = ServiceRequestItem
		fields = ['service', 'quantity']
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		excludes = ['ATAC-seq_24','ATAC-seq_96']
		self.fields['service'].queryset = ServiceInfo.objects.all().exclude(service_name__in=excludes)


class ServiceRequestCreationForm(forms.ModelForm):
	class Meta:
		model = ServiceRequest
		fields = ['notes']
		widgets = {
			'notes': forms.Textarea(attrs={'cols': 60, 'rows': 3}),
		}
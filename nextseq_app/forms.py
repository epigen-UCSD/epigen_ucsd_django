from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
#from django.utils.translation import gettext_lazy as _
from .models import RunInfo, LibrariesInRun
from django.forms import ModelForm

# class DateInput(forms.DateInput):
# 	input_type = 'date'


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        help_texts = {
            'username': '',
            'password1': '',
            'password2': ''
        }


class UserLoginForm(forms.Form):

    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class RunCreationForm(ModelForm):
    class Meta:
        model = RunInfo
        fields = ['Flowcell_ID', 'date', 'read_type',
                  'read_length', 'experiment_type','machine']
        widgets = {
            'date': forms.DateInput(),
            'experiment_type':forms.Select(attrs={'id':'nextseq_app_experiment_type'}),
            'machine': forms.Select(attrs={'id':'nextseq_app_machine'}),
            # 'read_type': forms.TextInput(attrs={'class': 'myfieldclass'}),
        }
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['machine'].queryset = SeqMachineInfo.objects.filter(sequencing_core__in=['EPIGEN','IGM'])

class LibrariesInRunForm(ModelForm):
    class Meta:
        model = LibrariesInRun
        fields = ['Library_ID', 'i7index', 'i5index']


class SamplesToCreatForm(forms.Form):
    samplestocreat = forms.CharField(
        label='Libraries to Save:',
        widget=forms.Textarea(attrs={'cols': 60, 'rows': 20}),
        initial='Sequencing_ID i7index i5index(separated by Space or Tab)\n'
    )

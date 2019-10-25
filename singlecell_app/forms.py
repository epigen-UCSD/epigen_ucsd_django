from django import forms
from django.forms import ModelForm, Textarea

from .models import CoolAdminSubmission

class CoolAdminForm(ModelForm):
    seqinfo = forms.CharField(
        label='Sequence',
        required=True,
        widget= forms.TextInput(attrs={
            'size':30,
            }),
        )
    class Meta:
        model = CoolAdminSubmission
        fields = ['pipeline_version',]
    
from django import forms
from django.forms import ModelForm, Textarea

from .models import CoolAdminSubmission

class CoolAdminForm(ModelForm):
    class Meta:
        model = CoolAdminSubmission
        fields = ['pipeline_version','useHarmony','snapUsePeak','snapSubset',
                    'doChromVar','readInPeak','tssPerCell','minReadPerCell',
                    'snapBinSize','snapNDims','date_submitted']
        exclude = ['seqinfo','status']
    
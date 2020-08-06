from django import forms
from django.forms import ModelForm, Textarea
from django.db import models
from masterseq_app.models import SeqInfo, GenomeInfo, RefGenomeInfo
from .models import CoolAdminSubmission

class CoolAdminForm(ModelForm):
    #refgenome = forms.ChoiceField(label='Reference Genome', choices=[(
        #x.genome_name, x.genome_name) for x in GenomeInfo.objects.all()])

    def __init__(self, *args, **kwargs):
        spec = kwargs.pop("spec", None)
        super(CoolAdminForm, self).__init__(*args, **kwargs)
        if spec:
            self.fields['refgenome'] = forms.ChoiceField(label='Reference Genome',
            choices=[(x.genome_name, x.genome_name) for x in GenomeInfo.objects.filter(species=spec)])
    class Meta:
        model = CoolAdminSubmission
        exclude = ['seqinfo','submitted','link']


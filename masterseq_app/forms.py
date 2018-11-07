from django import forms
from .models import SampleInfo,LibraryInfo,SeqMachineInfo
from django.contrib.auth.models import User
choice_for_read_type = (
	('SE','Single-end'),
	('PE','Paired-end'),
	('other (please explain in notes)','other (please explain in notes)'),
	)

class SampleCreationForm(forms.ModelForm):

	class Meta:
		model = SampleInfo
		fields = ['sample_id','date','species','sample_type','preparation','description','notes']
		widgets ={
			'date': forms.DateInput(),
			'description':forms.Textarea(attrs={'cols': 60, 'rows': 3}),
			'notes':forms.Textarea(attrs={'cols': 60, 'rows': 3}),

		}

class LibraryCreationForm(forms.ModelForm):

	class Meta:
		model = LibraryInfo
		fields = ['library_id','sampleinfo','date_started','date_completed','experiment_type','protocalinfo',\
		'reference_to_notebook_and_page_number','notes']
		widgets ={
			'date_started': forms.DateInput(),
			'date_completed':forms.DateInput(),
			'notes':forms.Textarea(attrs={'cols': 60, 'rows': 3}),

		}
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['sampleinfo'].queryset = SampleInfo.objects.order_by('-pk')

# class SequencingCreationForm(forms.Form):
# 	read_length = forms.CharField(label='read length:',required=False)
# 	machine = forms.ModelChoiceField(queryset=SeqMachineInfo.objects.all())
# 	read_type = forms.ChoiceField(label='read type',choices = choice_for_read_type)
# 	portion_of_lane = 











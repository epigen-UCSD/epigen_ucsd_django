from django import forms
from .models import SampleInfo,LibraryInfo,SeqMachineInfo,choice_for_read_type
from django.contrib.auth.models import User
import datetime
from nextseq_app.models import Barcode

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

class SeqCreationForm(forms.Form):
	machine = forms.ModelChoiceField(queryset=SeqMachineInfo.objects.all())	
	read_type = forms.ChoiceField(label='read type',choices = (('', '---------'),) +choice_for_read_type,required=False,)
	read_length = forms.CharField(label='read length:',required=False)
	date_submitted_for_sequencing = forms.DateField(initial=datetime.date.today,required=False)
	sequencinginfo = forms.CharField(
			label='SeqInfo in this run:',
			widget=forms.Textarea(attrs={'cols': 120, 'rows': 10}),
			required=False,
			initial='SeqID\tLibID\tdefault_label\tteam_member\tportion_of_lane\ti7index\ti5index\tnotes\n\n'
		)
	def clean_sequencinginfo(self):
		data = self.cleaned_data['sequencinginfo']
		invalidliblist= []
		invaliduserlist = []
		invalidbarcodelist = []
		invalidbarcodelist2 = []
		invalidpolane = []
		flaglib = 0
		flaguser = 0
		flagbarcode = 0
		flagbarcode2 = 0
		flagpolane = 0
		cleadata = []
		for lineitem in data.strip().split('\n'):
			if not lineitem.startswith('SeqID\tLibID') and lineitem != '\r':
				cleadata.append(lineitem)
				libid = lineitem.split('\t')[1]
				if not LibraryInfo.objects.filter(library_id=libid).exists():
					invalidliblist.append(libid)
					flaglib = 1
				membername = lineitem.split('\t')[3]
				if not User.objects.filter(username=membername).exists():
					invaliduserlist.append(membername)
					flaguser = 1
				try:
					indexname = lineitem.split('\t')[5]
					if indexname and not Barcode.objects.filter(indexid=indexname).exists():
						invalidbarcodelist.append(indexname)
						flagbarcode = 1
				except:
					pass
				try:
					indexname2 = lineitem.split('\t')[6]
					if indexname2 and not Barcode.objects.filter(indexid=indexname2).exists():
						invalidbarcodelist2.append(indexname)
						flagbarcode2 = 1
				except:
					pass
				if lineitem.split('\t')[4]:
					try:
						float(lineitem.split('\t')[4])
					except:
						invalidpolane.append(lineitem.split('\t')[4])
						flagpolane = 1		
		if flaglib == 1:
			raise forms.ValidationError('Invalid Library:'+','.join(invalidliblist))
		if flaguser == 1:
			raise forms.ValidationError('Invalid Member Name:'+','.join(invaliduserlist))
		if flagbarcode == 1:
			raise forms.ValidationError('Invalid i7 Barcode:'+','.join(invalidbarcodelist))
		if flagbarcode2 == 1:
			raise forms.ValidationError('Invalid i5 Barcode:'+','.join(invalidbarcodelist2))
		if flagpolane == 1:
			raise forms.ValidationError('Invalid portion of lane:'+','.join(invalidpolane))
		return '\n'.join(cleadata)











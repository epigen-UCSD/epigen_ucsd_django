from django import forms
from .models import SampleInfo,LibraryInfo,SeqMachineInfo,\
choice_for_read_type,choice_for_species,choice_for_sample_type,\
choice_for_preparation,choice_for_experiment_type
from django.contrib.auth.models import User
import datetime
from nextseq_app.models import Barcode
from epigen_ucsd_django.shared import datetransform,SelfUniqueValidation

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

class SamplesCreationForm(forms.Form):
	samplesinfo = forms.CharField(
			label='SampleInfo(Please copy and paste the columnA-V from TrackingSheet 1):',
			widget=forms.Textarea(attrs={'cols': 120, 'rows': 10}),
			required=False,
					)
	def clean_samplesinfo(self):
		data = self.cleaned_data['samplesinfo']
		cleaneddata = []
		flagdate = 0
		flagspecies = 0
		flagtype = 0
		flagindex = 0
		#flagprep = 0
		invaliddate = []
		invalidspecies = []
		invalidtype = []
		invalidindex = []
		#invalidprep = []
		for lineitem in data.strip().split('\n'):
			if lineitem != '\r':
				fields = lineitem.split('\t')
				try:
					samdate = datetransform(fields[0].strip())
				except:
					invaliddate.append(fields[0].strip())
					flagdate = 1
				samid = fields[8].strip()
				samdescript = fields[9].strip()
				samspecies = fields[10].split('(')[0].lower().strip()
				if samspecies not in [x[0].split('(')[0].strip() for x in choice_for_species]:
					invalidspecies.append(samspecies)
					flagspecies = 1
				samtype = fields[11].split('(')[0].strip()
				if samtype not in [x[0].split('(')[0].strip() for x in choice_for_sample_type]:
					invalidtype.append(samtype)
					flagtype = 1
				# samprep = fields[12].split('(')[0].strip()
				# if samprep == 'flash frozen':
				# 	samprep = 'flash frozen without cryopreservant'
				# 	# raise forms.ValidationError('Please denote whether the preparation is\
				# 	# 	flash frozen without cryopreservant or flash frozen with cryopreservant')
				# if samprep not in [x[0].split('(')[0].strip() for x in choice_for_preparation]:
				# 	invalidprep.append(samprep)
				# 	flagprep = 1
				samnotes = fields[20].strip()
				print(samnotes)
				samindex = fields[21].strip()
				if SampleInfo.objects.filter(sample_index=samindex).exists():
					invalidindex.append(samindex)
					flagindex = 1
					
				cleaneddata.append(lineitem)
		if flagdate == 1:
			raise forms.ValidationError('Invalid date:'+','.join(invaliddate)+'. Please enter like this: 10/30/2018')
		if flagspecies == 1:
			raise forms.ValidationError('Invalid species:'+','.join(invaliddate))
		if flagtype == 1:
			raise forms.ValidationError('Invalid sample type:'+','.join(invalidtype))
		if flagindex  == 1:
			raise forms.ValidationError(','.join(invalidindex)+' is already existed in database')
		# if flagprep == 1:
		# 	raise forms.ValidationError('Invalid sample preparation:'+','.join(invalidprep))
		return '\n'.join(cleaneddata)


class LibsCreationForm(forms.Form):
	libsinfo = forms.CharField(
			label='LibsInfo(Please copy and paste the columnA-M from TrackingSheet 2):',
			widget=forms.Textarea(attrs={'cols': 120, 'rows': 10}),
			required=False,
					)
	def clean_libsinfo(self):
		data = self.cleaned_data['libsinfo']
		cleaneddata = []
		flagsam = 0
		flagdate = 0
		flagexp = 0
		flaglibid = 0
		invalidsam = []
		invaliddate = []
		invalidexp = []
		selflibs = []
		invalidlibid =[]
		for lineitem in data.strip().split('\n'):
			if lineitem != '\r':
				cleaneddata.append(lineitem)
				fields = lineitem.split('\t')
				samindex = fields[0].strip()
				if not SampleInfo.objects.filter(sample_index=samindex).exists():
					invalidsam.append(samindex)
					flagsam = 1
				try:
					datestart = datetransform(fields[3].strip())					
				except:
					invaliddate.append(fields[3].strip())
					flagdate = 1
				try:
					dateend = datetransform(fields[4].strip())
				except:
					invaliddate.append(fields[4].strip())
					flagdate = 1
				libexp = fields[5].strip()
				if libexp not in [x[0].split('(')[0].strip() for x in choice_for_experiment_type]:
					invalidexp.append(libexp)
					flagexp = 1
				libid = fields[10].strip()
				if LibraryInfo.objects.filter(library_id=libid).exists():
					invalidlibid.append(libid)
					flaglibid = 1
					
				selflibs.append(libid)

		if flagsam == 1:
			raise forms.ValidationError('Invalid sample info:'+','.join(invalidsam))
		if flagdate == 1:
			raise forms.ValidationError('Invalid date:'+','.join(invaliddate))
		if flagexp == 1:
			raise forms.ValidationError('Invalid experiment type:'+','.join(invalidexp))
		if flaglibid == 1:
			raise forms.ValidationError(','.join(invalidlibid)+' is already existed in database')
		libraryselfduplicate = SelfUniqueValidation(selflibs)
		if len(libraryselfduplicate) > 0:
			raise forms.ValidationError('Duplicate Library within this bulk entry:'+','.join(libraryselfduplicate))

		return '\n'.join(cleaneddata)





from django import forms
from .models import SampleInfo, LibraryInfo, SeqMachineInfo, SeqInfo,\
    choice_for_read_type, choice_for_species, choice_for_sample_type,\
    choice_for_preparation, choice_for_experiment_type
from django.contrib.auth.models import User
import datetime
from nextseq_app.models import Barcode
from epigen_ucsd_django.shared import datetransform,SelfUniqueValidation
from django.shortcuts import get_object_or_404

class SampleCreationForm(forms.ModelForm):

	class Meta:
		model = SampleInfo
		fields = ['sample_id','date','species','sample_type','preparation',\
		'fixation','sample_amount','unit','service_requested',\
		'seq_depth_to_target','seq_length_requested','seq_type_requested','description','notes','status']
		widgets ={
			'date': forms.DateInput(),
			'description':forms.Textarea(attrs={'cols': 60, 'rows': 3}),
			'notes':forms.Textarea(attrs={'cols': 60, 'rows': 3}),
		}

class LibraryCreationForm(forms.ModelForm):
	sampleinfo = forms.ModelChoiceField(queryset=SampleInfo.objects.all(),widget=forms.TextInput({'class': 'ajax_sampleinput_form','size':50}))
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
		self.initial['sampleinfo'] = self.instance.sampleinfo.__str__

		#self.fields['sampleinfo'].queryset = SampleInfo.objects.order_by('-pk')
	# def clean(self):
	# def clean(self, *args, **kwargs):
	# 	data = self.data.copy()
	# 	if 'sampleinfo' in data:
	# 		#print(data['sampleinfo'])
	# 		obj = get_object_or_404(SampleInfo, sample_index=data['sampleinfo'].split(':')[0])
	# 		print(obj.id)
	# 		data['sampleinfo'] = str(obj.id)
	# 	self.data = data
	# 	print(self.data)
	# 	return super(LibraryCreationForm,self).clean()

	# 	if data is not None:
	# 		print(data)
	# 		data = data.copy()
	# 		if data['sampleinfo']:
	# 			obj = get_object_or_404(SampleInfo, sample_index=data['sampleinfo'].split(':')[0])
	# 			data['sampleinfo'] = obj.id
	# 			print(data['sampleinfo'])
	# 	super().clean(*args, **kwargs)
	# def save(self, commit=True):
	# 	instance = super().save(commit=False)
	# 	cleaned_sample = self.cleaned_data['sampleinfo']
	# 	if cleaned_sample:
	# 		f = get_object_or_404(SampleInfo,sample_index=cleaned_sample.split(':')[0])
	# 		instance.filename = f
	# 	else:
	# 		instance.filename = None
	# 	if commit:
	# 		instance.save()
	# 	return instance

class SeqCreationForm(forms.ModelForm):
	libraryinfo = forms.ModelChoiceField(queryset=LibraryInfo.objects.all(),widget=forms.TextInput({'class': 'ajax_libinput_form','size':50}))
	class Meta:
		model = SeqInfo
		fields = ['seq_id','libraryinfo','date_submitted_for_sequencing','machine','read_length','read_type',\
		'portion_of_lane','i7index','i5index','default_label','notes']
		widgets ={
			'date_submitted_for_sequencing': forms.DateInput(),
			'notes':forms.Textarea(attrs={'cols': 60, 'rows': 3}),
		}
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.initial['libraryinfo'] = self.instance.libraryinfo.__str__


class SeqCreationForm2(forms.Form):
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
			label='SampleInfo(Please copy and paste the columnA-V from TrackingSheet 1)',
			widget=forms.Textarea(attrs={'cols': 120, 'rows': 10}),
			required=True,
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
        required=True,
    )

    def clean_libsinfo(self):
        data = self.cleaned_data['libsinfo']
        cleaneddata = []
        flagsam = 0
        flagdate = 0
        flagexp = 0
        flaglibid = 0
        flaguser = 0
        invalidsam = []
        invaliddate = []
        invalidexp = []
        selflibs = []
        invalidlibid = []
        invaliduserlist = []
        for lineitem in data.strip().split('\n'):
            if lineitem != '\r':
                cleaneddata.append(lineitem)
                #print(lineitem)
                fields = lineitem.split('\t')
                samindex = fields[0].strip()
                if not SampleInfo.objects.filter(sample_index=samindex).exists() and not samindex.strip().lower() in ['na','other','n/a']:
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
                membername = fields[2].strip()
                if not User.objects.filter(username=membername).exists():
                    invaliduserlist.append(membername)
                    flaguser = 1

                selflibs.append(libid)

        if flagsam == 1:
            raise forms.ValidationError(
                'Invalid sample info:'+','.join(invalidsam))
        if flagdate == 1:
            raise forms.ValidationError('Invalid date:'+','.join(invaliddate))
        if flagexp == 1:
            raise forms.ValidationError(
                'Invalid experiment type:'+','.join(invalidexp))
        if flaglibid == 1:
            raise forms.ValidationError(
                ','.join(invalidlibid)+' is already existed in database')
        libraryselfduplicate = SelfUniqueValidation(selflibs)
        if len(libraryselfduplicate) > 0:
            raise forms.ValidationError(
                'Duplicate Library within this bulk entry:'+','.join(libraryselfduplicate))
        if flaguser == 1:
            raise forms.ValidationError(
                'Invalid Member Name:'+','.join(invaliduserlist))
        return '\n'.join(cleaneddata)


class SeqsCreationForm(forms.Form):
    seqsinfo = forms.CharField(
        label='SeqsInfo(Please copy and paste the columnA-R from TrackingSheet 3):',
        widget=forms.Textarea(attrs={'cols': 120, 'rows': 10}),
        required=True,
    )

    def clean_seqsinfo(self):
        data = self.cleaned_data['seqsinfo']
        cleaneddata = []
        flaglib = 0
        flagdate = 0
        flaguser = 0
        flagbarcode = 0
        flagbarcode2 = 0
        flagseqid = 0
        flagmachine = 0
        flagtype = 0
        flagpolane = 0
        invalidlib = []
        invaliddate = []
        invaliduserlist = []
        invalidbarcodelist = []
        invalidbarcodelist2 = []
        invalidseqid = []
        selfseqs = []
        invalidmachine = []
        invalidtype = []
        invalidpolane = []

        for lineitem in data.strip().split('\n'):
            if lineitem != '\r':
                cleaneddata.append(lineitem)
                fields = lineitem.split('\t')
                libraryid = fields[7].strip()
                exptype = fields[9].strip()
                if not LibraryInfo.objects.filter(library_id=libraryid).exists():
                    invalidlib.append(libraryid)
                    flaglib = 1

                if '-' in fields[6].strip():
                    datesub = fields[6].strip()
                else:
                    try:
                        datesub = datetransform(fields[6].strip())
                    except:
                        invaliddate.append(fields[6].strip())
                        flagdate = 1
                membername = fields[5].strip()
                if not User.objects.filter(username=membername).exists():
                    invaliduserlist.append(membername)
                    flaguser = 1

                indexname = fields[15].strip()
                if indexname and indexname not in ['NA', 'Other (please explain in notes)', 'N/A']:
                    if not Barcode.objects.filter(indexid=indexname).exists():
                        invalidbarcodelist.append(indexname)
                        flagbarcode = 1
                indexname2 = fields[16].strip()
                if indexname2 and indexname2 not in ['NA', 'Other (please explain in notes)', 'N/A']:
                    if not Barcode.objects.filter(indexid=indexname2).exists():
                        invalidbarcodelist2.append(indexname2)
                        flagbarcode2 = 1
                polane = fields[14].strip()
                if polane and polane not in ['NA', 'Other (please explain in notes)', 'N/A']:
                    try:
                        float(polane)
                    except:
                        invalidpolane.append(polane)
                        flagpolane = 1
                seqid = fields[8].strip()
                if SeqInfo.objects.filter(seq_id=seqid).exists():
                    invalidseqid.append(seqid)
                    flagseqid = 1
                selfseqs.append(seqid)
                seqcore = fields[10].split('(')[0].strip()
                seqmachine = fields[11].split('(')[0].strip()
                if not SeqMachineInfo.objects.filter(sequencing_core=seqcore, machine_name=seqmachine).exists():
                    invalidmachine.append(seqcore+'_'+seqmachine)
                    flagmachine = 1
                seqtype = fields[13].strip()
                if seqtype not in [x[0].split('(')[0].strip() for x in choice_for_read_type]:
                    invalidtype.append(seqtype)
                    flagtype = 1
        if flaglib == 1:
            raise forms.ValidationError(
                'Invalid library info:'+','.join(invalidlib))
        if flagdate == 1:
            raise forms.ValidationError('Invalid date:'+','.join(invaliddate))
        if flaguser == 1:
            raise forms.ValidationError(
                'Invalid Member Name:'+','.join(invaliduserlist))
        if flagbarcode == 1 and exptype not in ['scATAC-seq', 'snATAC-seq']:
            raise forms.ValidationError(
                'Invalid i7 Barcode:'+','.join(invalidbarcodelist))
        if flagbarcode2 == 1 and exptype not in ['scATAC-seq', 'snATAC-seq']:
            raise forms.ValidationError(
                'Invalid i5 Barcode:'+','.join(invalidbarcodelist2))
        if flagpolane == 1:
            raise forms.ValidationError(
                'Invalid portion of lane:'+','.join(invalidpolane))
        if flagseqid == 1:
            raise forms.ValidationError(
                ','.join(invalidseqid)+' is already existed in database')
        seqselfduplicate = SelfUniqueValidation(selfseqs)
        if len(seqselfduplicate) > 0:
            raise forms.ValidationError(
                'Duplicate Seq within this bulk entry:'+','.join(seqselfduplicate))
        if flagmachine == 1:
            raise forms.ValidationError(
                'Invalid seqmachine:'+','.join(invalidmachine))
        if flagtype == 1:
            raise forms.ValidationError(
                'Invalid read type:'+','.join(invalidtype))

        return '\n'.join(cleaneddata)

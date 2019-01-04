from django import forms
from masterseq_app.models import SeqInfo,GenomeInfo
from .models import LibrariesSetQC
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import BaseFormSet


def libraryparse(libraries):
	tosave_list = []
	for library in libraries.split(','):
		librarytemp = library.replace('\xe2\x80\x93','-').replace('\xe2\x80\x94','-').split('-')
		if len(librarytemp) > 1:
			prefix = librarytemp[0].strip().split('_')[0]
			try:
				suffix = librarytemp[0].strip().split('_',2)[2]
			except IndexError as e:
				#print(e)
				suffix = ''
			startlib = librarytemp[0].strip().split('_')
			endlib = librarytemp[1].strip().split('_')
			if len(startlib) == len(endlib):
				numberrange = [startlib[1],endlib[1]]
			else:
				numberrange =[startlib[1],endlib[0]]
			if int(numberrange[1])<int(numberrange[0]):
				raise forms.ValidationError('Please check the order: '+ library)
			if not suffix:
				tosave_list += ['_'.join([prefix,str(x)]) for x in range(int(numberrange[0]),int(numberrange[1])+1)]
			else:
				tosave_list += ['_'.join([prefix,str(x),suffix]) for x in range(int(numberrange[0]),int(numberrange[1])+1)]
		else:
			tosave_list.append(library.strip())

	return tosave_list

class LibrariesSetQCCreationForm(forms.ModelForm):
	collaborator = forms.ModelChoiceField(queryset=User.objects.all(),\
		widget=forms.TextInput({'class': 'ajax_userinput_form','size':50}),required=False)	
	class Meta:
		model = LibrariesSetQC
		fields = ['set_name','collaborator','date_requested','experiment_type','notes']
		widgets ={
			 'date_requested': forms.DateInput(),
			 'notes':forms.Textarea(attrs={'cols': 60, 'rows': 3}),

		}
	# def __init__(self, *args, **kwargs):
	# 	super().__init__(*args, **kwargs)
	# 	self.fields['collaborator'].queryset = User.objects.filter(groups__name='epigencollaborators')
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if self.instance.collaborator:
			self.initial['collaborator'] = str(self.instance.collaborator.id)+': '+self.instance.collaborator.first_name\
		+self.instance.collaborator.last_name+'('+\
		self.instance.collaborator.groups.all().first().name+')'


class LibrariesForm(forms.ModelForm):
	libraries = forms.ModelMultipleChoiceField(queryset=SeqInfo.objects.all(),
		widget=FilteredSelectMultiple("Libraries", is_stacked=False)
		)	

	class Media:
		css = {'all': ('/static/admin/css/widgets.css',), }
		js = ('/admin/jsi18n/',)	

	def __init__(self, parents=None, *args, **kwargs):
		super(LibrariesForm, self).__init__(*args, **kwargs)

class LibrariesToIncludeCreatForm(forms.Form):
	librariestoinclude = forms.CharField(
			label='Libraries to Include:',
			widget=forms.Textarea(attrs={'cols': 100, 'rows': 6}),
			initial='Please enter Sequencing_IDs separated by a comma(,), group the' \
			' libraries with consecutive numbers by concatenating the min and max'\
			' with dash(–) or hyphen(-), eg. AVD_173 - AVD_187,AVD_37, AVD_38:\n\n',
			required=False,
		)


	def clean_librariestoinclude(self):
		data = self.cleaned_data['librariestoinclude']
		tosave_list = []
		for libraries in data.strip().split('\n'):
			if not libraries.startswith('Please enter') and libraries != '\r':
				tosave_list = libraryparse(libraries)
		for item in tosave_list:
			if item:
				if not SeqInfo.objects.filter(seq_id=item).exists():
					raise forms.ValidationError(item+' is not a stored library.')
		return list(set(tosave_list))


class ChIPLibrariesToIncludeCreatForm(forms.Form):
	librariestoincludeInput = forms.CharField(
			label='Libraries to Include(Input):',
			widget=forms.Textarea(attrs={'cols': 20, 'rows': 2}),
			required=False,
		)
	librariestoincludeIP = forms.CharField(
			label='Libraries to Include(IP):',
			widget=forms.Textarea(attrs={'cols': 40, 'rows': 2}),
			required=False,
		)
		
	def clean_librariestoincludeInput(self):
		tosave_list = []
		data = self.cleaned_data['librariestoincludeInput']	
		for libraries in data.strip().split('\n'):
			if not libraries.startswith('Please enter') and libraries != '\r':
				tosave_list = libraryparse(libraries)
		for item in tosave_list:
			if item:
				if not SeqInfo.objects.filter(seq_id=item).exists():
					raise forms.ValidationError(item+' is not a stored library.')
		return list(set(tosave_list))
	def clean_librariestoincludeIP(self):
		tosave_list = []
		data = self.cleaned_data['librariestoincludeIP']		
		for libraries in data.strip().split('\n'):
			if not libraries.startswith('Please enter') and libraries != '\r':
				tosave_list = libraryparse(libraries)
		for item in tosave_list:
			if item:
				if not SeqInfo.objects.filter(seq_id=item).exists():
					raise forms.ValidationError(item+' is not a stored library.')
		return list(set(tosave_list))

class SeqLabelGenomeCreationForm(forms.Form):
	sequencingid = forms.CharField(label='Sequencing ID',disabled=True)
	speciesbelong = forms.CharField(label='Species',disabled=True,widget=forms.TextInput(attrs={'size': '8'}))
	genomeinthisset =forms.ChoiceField(label='Genome',choices = [(x.genome_name,x.genome_name) for x in GenomeInfo.objects.all()]) # [('hg38','hg38')])

	lableinthisset = forms.CharField(label='Label')
	def __init__(self, *args, **kwargs):
		self.thisspecies = kwargs.pop('thisspecies')
		self.thisspecies_list = kwargs.pop('thisspecies_list')
		super(SeqLabelGenomeCreationForm, self).__init__(*args, **kwargs)
		self.fields['genomeinthisset'] = forms.ChoiceField(label='Genome',
				choices = [(x.genome_name,x.genome_name) for x in GenomeInfo.objects.filter(species=self.thisspecies)]
				)

class BaseSeqLabelGenomeCreationFormSet(BaseFormSet):
	def get_form_kwargs(self, index):
		kwargs = super().get_form_kwargs(index)
		#print(kwargs['thisspecies_list'])
		#print(index)
		kwargs['thisspecies'] = kwargs['thisspecies_list'][index]
		return kwargs




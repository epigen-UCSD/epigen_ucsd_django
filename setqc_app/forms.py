from django import forms
from nextseq_app.models import LibrariesInRun
from .models import LibrariesSetQC
from django.contrib.admin.widgets import FilteredSelectMultiple

class LibrariesSetQCCreationForm(forms.ModelForm):

	class Meta:
		model = LibrariesSetQC
		fields = ['set_name','date_requested','experiment_type','notes']
		widgets ={
			 'date_requested': forms.DateInput(),
			 'notes':forms.Textarea(attrs={'cols': 60, 'rows': 3}),

		}

class LibrariesForm(forms.ModelForm):
	libraries = forms.ModelMultipleChoiceField(queryset=LibrariesInRun.objects.all(),
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
			initial='Please enter Library_IDs separated by a comma(,), group the' \
			' libraries with consecutive numbers by concatenating the min and max'\
			' with dash(–) or hyphen(-), eg. AVD_173 - AVD_187,AVD_37, AVD_38:\n\n'
		)


	def clean_librariestoinclude(self):
		data = self.cleaned_data['librariestoinclude']
		tosave_list = []
		for libraries in data.strip().split('\n'):
			if not libraries.startswith('Please enter') and libraries != '\r':
				for library in libraries.split(','):
					librarytemp = library.replace('\xe2\x80\x93','-').replace('\xe2\x80\x94','-').split('-')
					if len(librarytemp) > 1:
						prefix = librarytemp[0].strip().split('_')[0]
						try:
							suffix = librarytemp[0].strip().split('_',2)[2]
						except IndexError as e:
							print(e)
							suffix = ''
						numberrange = [x.strip().split('_')[1] for x in librarytemp]
						if int(numberrange[1])<int(numberrange[0]):
							raise forms.ValidationError('Please check the order: '+ library)

						if not suffix:
							tosave_list += ['_'.join([prefix,str(x)]) for x in range(int(numberrange[0]),int(numberrange[1])+1)]
						else:
							tosave_list += ['_'.join([prefix,str(x),suffix]) for x in range(int(numberrange[0]),int(numberrange[1])+1)]

					else:
						tosave_list.append(library.strip())
		for item in tosave_list:
			if item:
				if not LibrariesInRun.objects.filter(Library_ID=item).exists():
					raise forms.ValidationError(item+' is not a stored library.')
		return tosave_list










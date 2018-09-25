from django.db import models
from django.contrib.auth.models import User
from masterseq_app.models import SequencingInfo

# Create your models here.
class LibrariesSetQC(models.Model):
	set_name = models.CharField(max_length=200,unique=True)
	setID = models.CharField(max_length=20,unique=True)
	date_requested = models.DateField(help_text='If the datepicker is not working, \
		please enter in this form: yyyy-mm-dd, like 2018-04-03',blank=True,null=True)
	requestor = models.ForeignKey(User, on_delete=models.CASCADE)
	experiment_type_choice = (('ATAC-seq','ATAC-seq'),('ChIP-seq','ChIP-seq'), ('HiC','HiC'),('Other','Other'))
	experiment_type = models.CharField(max_length=10,choices=experiment_type_choice)
	libraries_to_include = models.ManyToManyField(SequencingInfo,related_name='reglibrary')
	libraries_to_include_forChIP = models.ManyToManyField(SequencingInfo,through='ChipLibraryInSet',related_name='chiplibrary')
	notes = models.TextField(blank=True)
	last_modified = models.DateTimeField(auto_now=True)
	url = models.URLField(blank=True)
	version = models.CharField(max_length=200,blank=True)
	status = models.CharField(max_length=200,blank=True,default='ClickToSubmit')
	def __str__(self):
		return self.set_name

class ChipLibraryInSet(models.Model):
	librariesetqc = models.ForeignKey(LibrariesSetQC, on_delete=models.CASCADE)
	sequencinginfo = models.ForeignKey(SequencingInfo, on_delete=models.CASCADE)
	group_number = models.CharField(max_length=10)
	is_input = models.BooleanField('Is it paired-end?', default=False)




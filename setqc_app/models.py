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
	experiment_type_choice = (('ATAC-seq','ATAC-seq'),('ChIP-seq','ChIP-seq'), ('HiC','HiC'),('other','other'))
	experiment_type = models.CharField(max_length=10,choices=experiment_type_choice)
	libraries_to_include = models.ManyToManyField(SequencingInfo)
	notes = models.TextField(blank=True)
	last_modified = models.DateTimeField(auto_now=True)
	url = models.URLField(blank=True)
	def __str__(self):
		return self.set_name




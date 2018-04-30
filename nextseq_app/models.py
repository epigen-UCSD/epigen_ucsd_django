from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Barcode(models.Model):
	indexid = models.CharField(max_length=200)
	indexseq = models.CharField(max_length=200)
	def __str__(self):
		return self.indexid

class RunInfo(models.Model):
	runid = models.CharField(max_length=200)
	operator = models.ForeignKey(User, on_delete=models.CASCADE)
	date = models.DateField('I did this run on...')
	is_pe = models.BooleanField('Is it paired-end?', default=True)
	reads_length = models.IntegerField(default=75)

	def get_absolute_url(self):
		return reverse('nextseq_app:rundetail', kwargs={'pk': self.pk})

	def __str__(self):
		return self.runid
class SamplesInRun(models.Model):
	singlerun = models.ForeignKey(RunInfo, on_delete=models.CASCADE)
	sampleid = models.CharField(max_length=200)
	i7index = models.ForeignKey(Barcode,related_name='i7_index', on_delete=models.CASCADE, blank=True,null=True)
	i5index = models.ForeignKey(Barcode,related_name='i5_index',on_delete=models.CASCADE, blank=True,null=True)
	def __str__(self):
	 	return self.sampleid

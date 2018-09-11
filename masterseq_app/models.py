from django.db import models

# Create your models here.
class SequencingInfo(models.Model):
	sequencing_id =  models.CharField(max_length=100,unique=True)

class SamplesInfo(models.Model):
	sample_id = models.CharField(max_length=100,unique=True)

class LibraryInfo(models.Model):
	library_id = models.CharField(max_length=100,unique=True)




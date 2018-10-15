from django.db import models

# Create your models here.

class ProtocalInfo(models.Model):
	protocal_name = models.CharField(max_length=50)	
	experiment_type_choice = (('ATAC-seq','ATAC-seq'),('ChIP-seq','ChIP-seq'), ('HiC','HiC'),('Other','Other'))
	experiment_type = models.CharField(max_length=10,choices=experiment_type_choice)
	def __str__(self):
		return self.protocal_name

class SequencingMachineInfo(models.Model):
	machine_name = models.CharField(max_length=50)
	sequencing_core = models.CharField(max_length=50)
	def __str__(self):
		return self.sequencing_core+'_'+self.machine_name

class GenomeInfo(models.Model):
	genome_name = models.CharField(max_length=50)
	species_choice = (('Human','Human'),('Mouse','Mouse'),('Other','Other'))
	species = models.CharField(max_length=10,choices=species_choice)

	def __str__(self):
		return self.species+'_'+self.genome_name

class SequencingInfo(models.Model):
	sequencing_id =  models.CharField(max_length=100,unique=True)

class SamplesInfo(models.Model):
	sample_id = models.CharField(max_length=100,unique=True)

class LibraryInfo(models.Model):
	library_id = models.CharField(max_length=100,unique=True)



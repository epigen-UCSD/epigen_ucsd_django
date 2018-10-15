from django.db import models
from django.contrib.auth.models import User
from nextseq_app.models import Barcode

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


class SampleInfo(models.Model):
	sample_id = models.CharField(max_length=100,unique=True)
	sample_index = models.CharField(max_length=20,blank=True)
	species_choice = (('Human','Human'),('Mouse','Mouse'),('Other','Other'))
	species = models.CharField(max_length=10,choices=species_choice)
	sample_type_choice = (
		('cultured cell','cultured cell'),
		('isolated nuclei','isolated nuclei'),
		('tissue','tissue'),
		('PcA cell line','PcA cell line'),
		('other','other')
		)
	sample_type = models.CharField(max_length=50,choices=sample_type_choice)
	preparation_choice = (
		('slow frozen with cryopreservant','slow frozen with cryopreservant'),
		('flash frozen','flash frozen'),
		('douncing homogenization','douncing homogenization'),
		('other','other')
		)
	preparation = models.CharField(max_length=10,choices=preparation_choice)
	description = models.CharField(max_length=10,blank=True)

class LibraryInfo(models.Model):
	library_id = models.CharField(max_length=100,unique=True)
	sampleinfo = models.ForeignKey(SampleInfo, on_delete=models.CASCADE,null=True)
	experiment_index = models.CharField(max_length=20,blank=True)
	experiment_type_choice = (('ATAC-seq','ATAC-seq'),('ChIP-seq','ChIP-seq'), ('HiC','HiC'),('Other','Other'))
	experiment_type = models.CharField(max_length=10,choices=experiment_type_choice,null=True)
	protocalinfo =  models.ForeignKey(ProtocalInfo, on_delete=models.CASCADE,null=True)
	reference_to_notebook_and_page_number = models.CharField(max_length=50,null=True)
	date_started = models.DateField(blank=True,null=True)
	date_completed = models.DateField(blank=True,null=True)
	team_member_initails = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	notes = models.CharField(max_length=10,blank=True)


class SequencingInfo(models.Model):
	sequencing_id =  models.CharField(max_length=100,unique=True)
	libraryinfo = models.ForeignKey(LibraryInfo, on_delete=models.CASCADE,null=True)
	team_member_initails = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	machine = models.ForeignKey(SequencingMachineInfo, on_delete=models.CASCADE,null=True)
	sequencing_length = models.CharField(max_length=50,blank=True)
	read_type_choice = (('SE','Single-end'),('PE','Paired-end'))
	read_type = models.CharField(max_length=2,choices=read_type_choice,null=True)
	portion_of_lane = models.FloatField(blank=True,null=True)
	i7index = models.ForeignKey(Barcode,related_name='sequencing_i7_index', on_delete=models.CASCADE, blank=True, null=True)
	i5index = models.ForeignKey(Barcode,related_name='sequencing_i5_index',on_delete=models.CASCADE, blank=True, null=True)


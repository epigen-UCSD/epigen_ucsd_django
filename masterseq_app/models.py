from django.db import models
from django.contrib.auth.models import User
from nextseq_app.models import Barcode

# Create your models here.


choice_for_experiment_type = (
	('ATAC-seq','ATAC-seq'),
	('ChIP-seq','ChIP-seq'),
	('Hi-C Arima Kit','Hi-C Arima Kit'),
	('Hi-C Epigen','Hi-C Epigen'),
	('scATAC-seq','scATAC-seq'),
	('scRNA-seq','scRNA-seq'),
	('snRNA-seq','snRNA-seq'),
	('4C','4C'),
	('CUT&RUN','CUT&RUN'),
	('Other','Other')
		)
choice_for_sample_type = (
	('cultured cells','cultured cells'),
	('isolated cells','isolated cells'),
	('isolated nuclei','isolated nuclei'),
	('PcA cell line','PcA cell line'),
	('tissue','tissue'),
	('other','other')
		)
choice_for_preparation = (
	('flash frozen without cryopreservant','flash frozen without cryopreservant'),
	('flash frozen with cryopreservant','flash frozen with cryopreservant'),
	('slow frozen with cryopreservant','slow frozen with cryopreservant'),
	('fresh','fresh'),
	('other','other')
		)
choice_for_read_type = (
	('SE','Single-end'),
	('PE','Paired-end')
	)
choice_for_species = (
	('Human','Human'),
	('Mouse','Mouse'),
	('Other','Other')
	)

class ProtocalInfo(models.Model):
	protocal_name = models.CharField(max_length=50)	
	experiment_type_choice = choice_for_experiment_type
	experiment_type = models.CharField(max_length=50,choices=experiment_type_choice)
	def __str__(self):
		return self.protocal_name

class SeqMachineInfo(models.Model):
	machine_name = models.CharField(max_length=50)
	sequencing_core = models.CharField(max_length=50)
	def __str__(self):
		return self.sequencing_core+'_'+self.machine_name

class GenomeInfo(models.Model):
	genome_name = models.CharField(max_length=50)
	species_choice = choice_for_species
	species = models.CharField(max_length=10,choices=species_choice)

	def __str__(self):
		return self.species+'_'+self.genome_name


class SampleInfo(models.Model):
	sample_id = models.CharField(max_length=100)
	sample_index = models.CharField(max_length=20,blank=True)
	species_choice = choice_for_species
	species = models.CharField(max_length=10,choices=species_choice)
	sample_type_choice = choice_for_sample_type
	sample_type = models.CharField(max_length=50,choices=sample_type_choice)
	preparation_choice = choice_for_preparation
	preparation = models.CharField(max_length=50,choices=preparation_choice)
	description = models.TextField(blank=True)
	notes = models.TextField(blank=True)


class LibraryInfo(models.Model):
	library_id = models.CharField(max_length=100,unique=True)
	sampleinfo = models.ForeignKey(SampleInfo, on_delete=models.CASCADE,null=True)
	experiment_index = models.CharField(max_length=20,blank=True)
	experiment_type_choice = choice_for_experiment_type
	experiment_type = models.CharField(max_length=10,choices=experiment_type_choice,null=True)
	protocalinfo =  models.ForeignKey(ProtocalInfo, on_delete=models.CASCADE,null=True)
	reference_to_notebook_and_page_number = models.CharField(max_length=50,null=True)
	date_started = models.DateField(blank=True,null=True)
	date_completed = models.DateField(blank=True,null=True)
	team_member_initails = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	notes = models.TextField(blank=True)


class SeqInfo(models.Model):
	seq_id =  models.CharField(max_length=100,unique=True)
	libraryinfo = models.ForeignKey(LibraryInfo, on_delete=models.CASCADE,null=True)
	team_member_initails = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
	machine = models.ForeignKey(SeqMachineInfo, on_delete=models.CASCADE,null=True)
	read_length = models.CharField(max_length=50,blank=True)
	read_type_choice = choice_for_read_type
	read_type = models.CharField(max_length=2,choices=read_type_choice,null=True)
	portion_of_lane = models.FloatField(blank=True,null=True)
	i7index = models.ForeignKey(Barcode,related_name='sequencing_i7_index', on_delete=models.CASCADE, blank=True, null=True)
	i5index = models.ForeignKey(Barcode,related_name='sequencing_i5_index',on_delete=models.CASCADE, blank=True, null=True)
	total_reads = models.IntegerField(blank=True,null=True)

class SeqBioInfo(models.Model):
	seqinfo = models.ForeignKey(SeqInfo, on_delete=models.CASCADE)
	genome  =  models.ForeignKey(GenomeInfo, on_delete=models.CASCADE,blank=True,null=True)
	pipeline_version = models.CharField(max_length=200,blank=True)
	final_reads = models.IntegerField(blank=True,null=True)
	final_yield = models.FloatField(blank=True,null=True)
	mito_frac = models.FloatField(blank=True,null=True)
	tss_enrichment = models.FloatField(blank=True,null=True)
	frop = models.FloatField(blank=True,null=True)





from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Barcode(models.Model):
    indexid = models.CharField(max_length=200, unique=True)
    indexseq = models.CharField(max_length=200)

    def __str__(self):
        return self.indexid

    class Meta:
        ordering = ['indexid']


class RunInfo(models.Model):
    # runid = models.CharField(max_length=200,unique=True,help_text='Please enter the flowcellSe')
    Flowcell_ID = models.CharField(
        max_length=200, unique=True, help_text='Please enter the FlowcellSerialNumber, like H5GLYBGX5')
    operator = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField('I did this run on...',
                            help_text='If the datepicker is not working, please enter in this form: yyyy-mm-dd, like 2018-04-03', blank=True, null=True)
    read_type_choice = (('SE', 'Single-end'), ('PE', 'Paired-end'))
    exp_type_choice = (('BK', 'bulk'), ('SN', 'snATAC'),
                       ('TA', '10xATAC'), ('TR', '10xRNA'))
    read_type = models.CharField(
        max_length=2, choices=read_type_choice, default='PE', help_text='default:PE')
    experiment_type = models.CharField(max_length=2, choices=exp_type_choice,
                                       default='BK', help_text='bulk (default), snATAC:combinatory barcode, 10xATAC, 10xRNAseq')
    total_reads = models.IntegerField(blank=True, null=True)
    total_libraries = models.IntegerField(blank=True, null=True)
    percent_of_reads_demultiplexed = models.IntegerField(blank=True, null=True)
    read_length = models.CharField(
        max_length=50, help_text='e.g. if R1=R2=75, enter 75, if R1=50,R2=75, enter 50+75')
    updated_at = models.DateTimeField(auto_now=True)
    nextseqdir = models.CharField(max_length=200, blank=True, null=True)

    jobstatus = models.CharField(
        max_length=200, blank=True, null=True, default='ClickToSubmit')

    def get_absolute_url(self):
        return reverse('nextseq_app:rundetail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.Flowcell_ID

    class Meta:
        ordering = ['-date']


class LibrariesInRun(models.Model):
    singlerun = models.ForeignKey(RunInfo, on_delete=models.CASCADE)
    Library_ID = models.CharField(max_length=200, unique=True)
    i7index = models.ForeignKey(Barcode, related_name='i7_index',
                                on_delete=models.CASCADE, blank=True, null=True)
    i5index = models.ForeignKey(Barcode, related_name='i5_index',
                                on_delete=models.CASCADE, blank=True, null=True)
    numberofreads = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.Library_ID

    class Meta:
        ordering = ['Library_ID']

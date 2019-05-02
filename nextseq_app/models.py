from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

choice_for_machine = (
    ('EPIGEN_NextSeq550', 'EPIGEN_NextSeq550'),
    ('IGM_HiSeq4000', 'IGM_HiSeq4000'),
)


class Barcode(models.Model):
    indexid = models.CharField(max_length=200, unique=True)
    indexseq = models.CharField(max_length=200)
    kit_choice = (('BK', 'bulk'), ('S2', 'snATAC_v2'),
                  ('TA', '10xATAC'), ('TR', '10xRNA'),
                  ('BT', 'bulk_10xATAC'))
    kit = models.CharField(
        max_length=2, choices=kit_choice, default='BK', help_text='bulk (default), snATAC_v2:combinatory barcode v2, 10xATAC, 10xRNAseq')

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
    exp_type_choice = (('BK', 'bulk'), ('S2', 'snATAC_v2'),
                       ('TA', '10xATAC'), ('TR', '10xRNA'), ('BT', 'bulk_10xATAC'))
    read_type = models.CharField(
        max_length=2, choices=read_type_choice, default='PE', help_text='default:PE')
    experiment_type = models.CharField(max_length=2, choices=exp_type_choice,
                                       default='BK', help_text='bulk (default), snATAC_v2:combinatory barcode v2, 10xATAC, 10xRNAseq, bulk_10xATAC')
    total_reads = models.IntegerField(blank=True, null=True)
    total_libraries = models.IntegerField(blank=True, null=True)
    percent_of_reads_demultiplexed = models.IntegerField(blank=True, null=True)
    read_length = models.CharField(
        max_length=50, help_text='Bulk: one number(eg. 75); Single-cell: R1+I1+I2+R2 (eg:50+8+16+50)')
    updated_at = models.DateTimeField(auto_now=True)
    nextseqdir = models.CharField(max_length=200, blank=True, null=True)
    # machine = models.ForeignKey('masterseq_app.SeqMachineInfo', on_delete=models.CASCADE, null=True)
    machine = models.CharField(
        max_length=50, choices=choice_for_machine, default='EPIGEN_NextSeq550', null=True)
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
    lane = models.CharField(max_length=20,blank=True, null=True)

    def __str__(self):
        return self.Library_ID

    class Meta:
        ordering = ['Library_ID']

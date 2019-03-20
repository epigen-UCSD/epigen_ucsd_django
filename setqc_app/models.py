from django.db import models
from django.contrib.auth.models import User,Group
from masterseq_app.models import SeqInfo,GenomeInfo

# Create your models here.


class LibrariesSetQC(models.Model):
    set_name = models.CharField(max_length=200, unique=True)
    set_id = models.CharField(max_length=20, unique=True)
    date_requested = models.DateField(help_text='If the datepicker is not working, \
		please enter in this form: yyyy-mm-dd, like 2018-04-03', blank=True, null=True)
    requestor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='requestor')
    experiment_type_choice = (
        ('ATAC-seq', 'ATAC-seq'), ('ChIP-seq', 'ChIP-seq'), ('HiC', 'HiC'), ('Other (please explain in notes)', 'Other (please explain in notes)'))
    experiment_type = models.CharField(
        max_length=50, choices=experiment_type_choice)
    libraries_to_include = models.ManyToManyField(
        SeqInfo, through='LibraryInSet')
    notes = models.TextField(blank=True)
    comments = models.TextField(blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    url = models.URLField(blank=True)
    version = models.CharField(max_length=200, blank=True)
    status = models.CharField(
        max_length=200, blank=True, default='ClickToSubmit')
    collaborator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='collaborator', blank=True, null=True)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.set_name


class LibraryInSet(models.Model):
    librariesetqc = models.ForeignKey(LibrariesSetQC, on_delete=models.CASCADE)
    seqinfo = models.ForeignKey(
        SeqInfo, on_delete=models.CASCADE, blank=True, null=True)
    group_number = models.CharField(max_length=10, blank=True)
    is_input = models.NullBooleanField('Is it input?', blank=True)
    label = models.CharField(max_length=100, blank=True)
    genome = models.ForeignKey(
        GenomeInfo, on_delete=models.CASCADE, blank=True, null=True)

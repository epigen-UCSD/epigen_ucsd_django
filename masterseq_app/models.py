from django.db import models
from django.contrib.auth.models import User, Group
from nextseq_app.models import Barcode
from epigen_ucsd_django.models import CollaboratorPersonInfo
# Create your models here.


choice_for_experiment_type = (
    ('ATAC-seq', 'ATAC-seq'),
    ('10xATAC', '10xATAC'),
    ('ChIP-seq', 'ChIP-seq'),
    ('Hi-C', 'Hi-C'),
    ('scATAC-seq', 'scATAC-seq'),
    ('scRNA-seq', 'scRNA-seq'),
    ('snRNA-seq', 'snRNA-seq'),
    ('4C', '4C'),
    ('CUT&RUN', 'CUT&RUN'),
    ('other (please explain in notes)', 'other (please explain in notes)')
)
choice_for_sample_type = (
    ('cultured cells', 'cultured cells'),
    ('isolated cells', 'isolated cells'),
    ('isolated nuclei', 'isolated nuclei'),
    ('tissue', 'tissue'),
    ('other (please explain in notes)', 'other (please explain in notes)')
)
choice_for_preparation = (
    ('flash frozen', 'flash frozen'),
    ('flash frozen with cryopreservant', 'flash frozen with cryopreservant'),
    ('slow frozen with cryopreservant', 'slow frozen with cryopreservant'),
    ('fresh', 'fresh'),
    ('other (please explain in notes)', 'other (please explain in notes)')
)
choice_for_read_type = (
    ('SE', 'Single-end'),
    ('PE', 'Paired-end'),
    ('other (please explain in notes)', 'other (please explain in notes)'),
)
choice_for_species = (
    ('human', 'Human'),
    ('mouse', 'Mouse'),
    ('rat', 'rat'),
    ('cattle','cattle'),
    ('monkey','monkey'),
    ('other (please explain in notes)', 'other (please explain in notes)')
)
choice_for_unit = (
    ('cells', 'cells'),
    ('mg', 'mg'),
    ('nuclei', 'nuclei'),
    ('other (please explain in notes)', 'other (please explain in notes)')

)
choice_for_fixation = (
    ('Yes (1% FA)', 'Yes (1% FA)'),
    ('No', 'No'),
    ('other (please explain in notes)', 'other (please explain in notes)')
)


class ProtocalInfo(models.Model):
    protocal_name = models.CharField(max_length=50)
    experiment_type_choice = choice_for_experiment_type
    experiment_type = models.CharField(
        max_length=50, choices=experiment_type_choice)

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
    species = models.CharField(max_length=10, choices=species_choice)

    def __str__(self):
        return self.genome_name


class SampleInfo(models.Model):
    sample_id = models.CharField('sample name', max_length=100)
    date = models.DateField(
        help_text='If the datepicker is not working, please enter in this form: yyyy-mm-dd, like 2018-04-03', blank=True, null=True)
    date_received = models.DateField(
        help_text='If the datepicker is not working, please enter in this form: yyyy-mm-dd, like 2018-04-03', blank=True, null=True)
    team_member = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    sample_index = models.CharField(max_length=30, blank=True)
    species_choice = choice_for_species
    species = models.CharField(max_length=10, choices=species_choice)
    sample_type_choice = choice_for_sample_type
    sample_type = models.CharField(max_length=50, choices=sample_type_choice)
    preparation_choice = choice_for_preparation
    preparation = models.CharField(max_length=50, choices=preparation_choice)
    description = models.TextField(blank=True)
    fixation_choice = choice_for_fixation
    fixation = models.CharField(
        max_length=50, choices=choice_for_fixation, null=True)
    notes = models.TextField(blank=True)
    internal_notes = models.TextField('Internal Notes',blank=True)
    sample_amount = models.CharField(max_length=100, blank=True, null=True)
    unit_choice = choice_for_unit
    unit = models.CharField(max_length=50, choices=unit_choice, null=True)
    storage = models.CharField(max_length=50, blank=True, null=True)
    experiment_type_choice = choice_for_experiment_type
    service_requested = models.CharField(
        max_length=50, choices=experiment_type_choice, null=True)
    seq_depth_to_target = models.CharField(
        max_length=50, blank=True, null=True)
    seq_length_requested = models.CharField(
        max_length=50, blank=True, null=True)
    seq_type_requested = models.CharField(max_length=50, blank=True, null=True)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, blank=True, null=True)
    research_name = models.CharField(max_length=200, blank=True, null=True)
    research_email = models.CharField(max_length=200, blank=True, null=True)
    research_phone = models.CharField(max_length=200, blank=True, null=True)
    fiscal_name = models.CharField(max_length=200, blank=True, null=True)
    fiscal_email = models.CharField(max_length=200, blank=True, null=True)
    fiscal_index = models.CharField(max_length=200, blank=True, null=True)

    research_person = models.ForeignKey(
        CollaboratorPersonInfo, related_name='contact_person', on_delete=models.CASCADE, null=True)
    fiscal_person = models.ForeignKey(
        CollaboratorPersonInfo, related_name='fiscal_person', on_delete=models.CASCADE, null=True)
    #fiscal_person_index = models.ForeignKey(Person_Index,on_delete=models.CASCADE,blank=True,null=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.sample_index+':'+self.sample_id


class LibraryInfo(models.Model):
    library_id = models.CharField('library name', max_length=100)
    library_description = models.TextField(blank=True)
    sampleinfo = models.ForeignKey(
        SampleInfo, on_delete=models.CASCADE, null=True)
    experiment_index = models.CharField(max_length=20, blank=True)
    experiment_type_choice = choice_for_experiment_type
    experiment_type = models.CharField(
        max_length=50, choices=experiment_type_choice, null=True)
    protocalinfo = models.ForeignKey(
        ProtocalInfo, on_delete=models.CASCADE, null=True)
    protocal_used = models.CharField(max_length=200,blank=True,null=True)
    reference_to_notebook_and_page_number = models.CharField(
        max_length=50, null=True)
    date_started = models.DateField(
        help_text='If the datepicker is not working, please enter in this form: yyyy-mm-dd, like 2018-04-03', blank=True, null=True)
    date_completed = models.DateField(
        help_text='If the datepicker is not working, please enter in this form: yyyy-mm-dd, like 2018-04-03', blank=True, null=True)
    team_member_initails = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.library_id


class SeqInfo(models.Model):
    seq_id = models.CharField(max_length=100, unique=True)
    libraryinfo = models.ForeignKey(
        LibraryInfo, on_delete=models.CASCADE, null=True)
    team_member_initails = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True)
    machine = models.ForeignKey(
        SeqMachineInfo, on_delete=models.CASCADE, null=True)
    read_length = models.CharField(max_length=50, blank=True)
    read_type_choice = choice_for_read_type
    read_type = models.CharField(
        max_length=50, choices=read_type_choice, null=True)
    portion_of_lane = models.FloatField(blank=True, null=True)
    i7index = models.ForeignKey(Barcode, related_name='sequencing_i7_index',
                                on_delete=models.CASCADE, blank=True, null=True)
    i5index = models.ForeignKey(Barcode, related_name='sequencing_i5_index',
                                on_delete=models.CASCADE, blank=True, null=True)
    total_reads = models.IntegerField(blank=True, null=True)
    date_submitted_for_sequencing = models.DateField(
        help_text='If the datepicker is not working, please enter in this form: yyyy-mm-dd, like 2018-04-03', blank=True, null=True)
    default_label = models.CharField(
        'Default Label(for setQC report)', max_length=200, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.seq_id


class SeqBioInfo(models.Model):
    seqinfo = models.ForeignKey(SeqInfo, on_delete=models.CASCADE)
    genome = models.ForeignKey(
        GenomeInfo, on_delete=models.CASCADE, blank=True, null=True)
    pipeline_version = models.CharField(max_length=200, blank=True)
    final_reads = models.IntegerField(blank=True, null=True)
    final_yield = models.FloatField(blank=True, null=True)
    mito_frac = models.FloatField(blank=True, null=True)
    tss_enrichment = models.FloatField(blank=True, null=True)
    frop = models.FloatField(blank=True, null=True)

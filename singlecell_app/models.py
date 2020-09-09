from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# Create your models here.


class CoolAdminSubmission(models.Model):
    V4 = 'v4'
    V2 = 'v2'
    pipeline_versions_choices = [
        (V2, 'v2'),
        (V4, 'v4'),
    ]

    submitted = models.BooleanField(default=False)
    pipeline_status = models.CharField(max_length=20, default='ClickToSubmit')
    pipeline_version = models.CharField(
        max_length=2, choices=pipeline_versions_choices, default=V2)
    seqinfo = models.ForeignKey(
        'masterseq_app.SeqInfo', on_delete=models.CASCADE, blank=False, null=True)
    refgenome = models.CharField(max_length=10, blank=True, null=True)
    date_submitted = models.DateTimeField(blank=True, null=True)
    date_modified = models.DateTimeField(blank=True, null=True)
    ''' Optional Parameters to be included later'''
    # USEHARMONY (default False, true if set to True) Perform harmony batch correction using the dataset IDs as batch IDs (Only used with 10x_model_multiple_projects.bash)
    useHarmony = models.BooleanField(default=False)

    # SNAPUSEPEAK (default False, true if set to True) Construct a peak matrix in addition to the bin matrix
    snapUsePeak = models.BooleanField(default=False)
    # SNAPSUBSET default empty or 0. Should be interger). Use this number to construct a subset that is used to construct the distance matrix for SNAP. The lower it is, the lesser is the resolution. After 10-15K cells, the memory might become an issue
    snapSubset = models.PositiveIntegerField(default=0)
    # DOCHROMVAR (default False, true if set to True). Perform chromVAR analysis
    doChromVar = models.BooleanField(default=False)
    # READINPEAK (default empty or default value: 0. Should be 0 < float < 1). QC metric used to filter cells with low ratio of reads in peak
    readInPeak = models.FloatField(default=0)
    # TSSPERCELL (default empty or default value: 7. Should be float ). QC metric used to filter cells with low TSS
    tssPerCell = models.FloatField(default=7)
    # MINNBREADPERCELL (default empty or default value: 500. Should be int ). QC metric used to filter cells with low number of aligned fragments
    minReadPerCell = models.IntegerField(default=500)
    # SNAPBINSIZE (default empty or default value: 5000 100000. Should be a list of int values separated by a blank). Determine the bins used to perform SNAP clustering.
    snapBinSize = models.CharField(default='5000 100000', max_length=100)
    # SNAPNDIMS (default empty or default value: 25. Should be a list of int values separated by a blank). Determine the number of dimensions to use to perform SNAP clustering.
    snapNDims = models.CharField(default="25", max_length=100)
    # link for cooladmin portal
    link = models.CharField(max_length=280, blank=True, null=True)


class CommonQCInfo(models.Model):
    estimated_cell_count = models.PositiveIntegerField()

    class Meta:
        abstract = True


class scRNAqcInfo(models.Model):
    estimated_number_of_cells = models.PositiveIntegerField()
    mean_reads_per_cell = models.PositiveIntegerField()
    median_genes_per_cell = models.PositiveIntegerField()
    number_of_reads = models.PositiveIntegerField()
    valid_barcodes = models.DecimalField(max_digits=20, decimal_places=16)
    sequencing_saturation = models.DecimalField(
        max_digits=20, decimal_places=16)
    q30_bases_in_barcode = models.DecimalField(
        max_digits=20, decimal_places=16)
    q30_bases_in_rna_read = models.DecimalField(
        max_digits=20, decimal_places=16)
    q30_bases_in_sample_index = models.DecimalField(null=True, blank=True, 
        max_digits=20, decimal_places=16)
    q30_bases_in_UMI = models.DecimalField(max_digits=20, decimal_places=16)
    reads_mapped_to_genome = models.DecimalField(
        max_digits=20, decimal_places=16)
    reads_mapped_confidently_to_genome = models.DecimalField(
        max_digits=20, decimal_places=16)
    reads_mapped_confidently_to_intergenic_regions = models.DecimalField(
        max_digits=20, decimal_places=16)
    reads_mapped_confidently_to_intronic_regions = models.DecimalField(
        max_digits=20, decimal_places=16)
    reads_mapped_confidently_to_exonic_regions = models.DecimalField(
        max_digits=20, decimal_places=16)
    reads_mapped_confidently_to_transcriptome = models.DecimalField(
        max_digits=20, decimal_places=16)
    reads_mapped_antisense_to_gene = models.DecimalField(
        max_digits=20, decimal_places=16)
    frac_reads_in_cells = models.DecimalField(max_digits=20, decimal_places=16)
    total_genes_detected = models.PositiveIntegerField()
    median_UMI_counts_per_cell = models.PositiveIntegerField()


class TenxqcInfo(models.Model):
    annotated_cells = models.PositiveIntegerField()
    bc_q30_bases_fract = models.DecimalField(max_digits=20, decimal_places=16)
    cellranger_atac_version = models.CharField(max_length=10)
    cells_detected = models.PositiveIntegerField()
    frac_cut_fragments_in_peaks = models.DecimalField(
        max_digits=20, decimal_places=16)
    frac_fragments_nfr = models.DecimalField(max_digits=20, decimal_places=16)
    frac_fragments_nfr_or_nuc = models.DecimalField(
        max_digits=20, decimal_places=16)
    frac_fragments_nuc = models.DecimalField(max_digits=20, decimal_places=16)
    frac_fragments_overlapping_peaks = models.DecimalField(
        max_digits=20, decimal_places=16)
    frac_fragments_overlapping_targets = models.DecimalField(
        max_digits=20, decimal_places=16)
    frac_mapped_confidently = models.DecimalField(
        max_digits=20, decimal_places=16)
    frac_waste_chimeric = models.DecimalField(max_digits=20, decimal_places=16)
    frac_waste_duplicate = models.DecimalField(
        max_digits=20, decimal_places=16)
    frac_waste_lowmapq = models.DecimalField(max_digits=20, decimal_places=16)
    frac_waste_mitochondrial = models.DecimalField(
        max_digits=20, decimal_places=16)
    frac_waste_no_barcode = models.DecimalField(
        max_digits=20, decimal_places=16)
    frac_waste_non_cell_barcode = models.DecimalField(
        max_digits=20, decimal_places=16)
    frac_waste_overall_nondup = models.DecimalField(
        max_digits=20, decimal_places=16)
    frac_waste_total = models.DecimalField(max_digits=20, decimal_places=16)
    frac_waste_unmapped = models.DecimalField(max_digits=20, decimal_places=16)
    median_fragments_per_cell = models.DecimalField(
        max_digits=20, decimal_places=16)
    num_fragments = models.PositiveIntegerField()
    r1_q30_bases_fract = models.DecimalField(max_digits=20, decimal_places=16)
    r2_q30_bases_fract = models.DecimalField(max_digits=20, decimal_places=16)
    si_q30_bases_fract = models.DecimalField(max_digits=20, decimal_places=16)
    total_usable_fragments = models.PositiveIntegerField()
    tss_enrichment_score = models.DecimalField(
        max_digits=20, decimal_places=16)


class SingleCellObject(models.Model):
    seqinfo = models.ForeignKey(
        'masterseq_app.SeqInfo', on_delete=models.CASCADE, blank=False, null=True)
    cooladminsubmission = models.ForeignKey(
        CoolAdminSubmission, null=True, blank=True, on_delete=models.CASCADE)
    qc_metrics = GenericForeignKey('content_type', 'object_id')
    experiment_type = models.CharField(max_length=10)
    date_last_modified = models.DateField(blank=True, null=True)
    tenx_pipeline_status = models.CharField(
        max_length=20, default='ClickToSubmit')
    path_to_websummary = models.CharField(max_length=100, blank=True)
    random_string_link = models.CharField(max_length=50, blank=True)
    # generic type foriegn key fields
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_id = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.seqinfo)

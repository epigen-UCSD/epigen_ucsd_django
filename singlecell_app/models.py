from django.db import models
from masterseq_app.models import SeqInfo

# Create your models here.

class CoolAdminSubmission(models.Model):
    V4 = 'V4'
    V2 = 'V2'
    pipeline_versions_choices = [
        (V4, 'V4'),
        (V2, 'V2'),
    ]
    pipeline_version = models.CharField(max_length=2,choices=pipeline_versions_choices,default=V4)
    seqinfo = models.ForeignKey(
        SeqInfo, on_delete=models.CASCADE, blank=False, null=True)
    genotype = models.CharField(max_length=6)
    date_submitted = models.DateTimeField(auto_now=True)

    ''' Optional Parameters to be included later
    # Size of the bin used for snap pipeline
    SNAPBINSIZE="5000 10000" # List of int
    # Use as subsetting strategy to perform snap pipeline
    SNAPSUBSETTING=10000 # Int representing the number of cells to use to create the ref map
    # List of number of dimensions to perform reduction
    SNAPNDIMS="25 50" # List of int
    # Number of neighbors to use to perform KNN prior to clustering
    SNAPNEIGH="15" # int

     '''   
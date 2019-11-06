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
    
    status = models.CharField(
        max_length=200, blank=True, default='ClickToSubmit')
    pipeline_version = models.CharField(max_length=2,choices=pipeline_versions_choices,default=V4)
    seqinfo = models.ForeignKey(
        SeqInfo, on_delete=models.CASCADE, blank=False, null=True)
    date_submitted = models.DateTimeField(blank=True, null=True)
    date_modified = models.DateTimeField(auto_now=True)
    ''' Optional Parameters to be included later'''
    #USEHARMONY (default False, true if set to True) Perform harmony batch correction using the dataset IDs as batch IDs (Only used with 10x_model_multiple_projects.bash)
    useHarmony =  models.BooleanField(default=False)

    #SNAPUSEPEAK (default False, true if set to True) Construct a peak matrix in addition to the bin matrix
    snapUsePeak = models.BooleanField(default=False)

    #SNAPSUBSET (default empty or 0. Should be interger). Use this number to construct a subset that is used to construct the distance matrix for SNAP. The lower it is, the lesser is the resolution. After 10-15K cells, the memory might become an issue
    snapSubset = models.PositiveIntegerField(default=0)

    #DOCHROMVAR (default False, true if set to True). Perform chromVAR analysis
    doChromVar = models.BooleanField(default=False)
    #READINPEAK (default empty or default value: 0. Should be 0 < float < 1). QC metric used to filter cells with low ratio of reads in peak
    readInPeak = models.FloatField(default=0)
    #TSSPERCELL (default empty or default value: 7. Should be float ). QC metric used to filter cells with low TSS
    tssPerCell = models.FloatField(default=7)
    #MINNBREADPERCELL (default empty or default value: 500. Should be int ). QC metric used to filter cells with low number of aligned fragments
    minReadPerCell = models.IntegerField(default=500)
    #SNAPBINSIZE (default empty or default value: 5000 100000. Should be a list of int values separated by a blank). Determine the bins used to perform SNAP clustering.
    snapBinSize = models.CharField(default='5000 100000', max_length=100)
    #SNAPNDIMS (default empty or default value: 25. Should be a list of int values separated by a blank). Determine the number of dimensions to use to perform SNAP clustering.
    snapNDims = models.CharField(default="25", max_length=100)
    
    @classmethod
    def create(cls, dict):
        submission = cls(
            pipeline_version=dict['pipeline_version'],
            seqinfo = dict['seqinfo'],
            useHarmony =  dict['useHarmony'],
            snapUsePeak = dict['snapUsePeak'],
            snapSubset = dict['snapSubset'],
            doChromVar = dict['doChromVar'],
            readInPeak = dict['readInPeak'],
            tssPerCell = dict['tssPerCell'],
            minReadPerCell = dict['minReadPerCell'],
            snapBinSize = dict['snapBinSize'],
            snapNDims = dict['snapNDims']    
        )
        return submission
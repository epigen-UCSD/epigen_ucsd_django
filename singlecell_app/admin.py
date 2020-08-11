from django.contrib import admin
from .models import CoolAdminSubmission, SingleCellObject, scRNAqcInfo, TenxqcInfo
# Register your models here.

@admin.register(CoolAdminSubmission)
class SCAdmin(admin.ModelAdmin):
    list_display = ('seqinfo', 'pipeline_version', 'date_submitted', 'date_modified', 'date_submitted', 'link','submitted')


@admin.register(SingleCellObject)
class SCObjAdmin(admin.ModelAdmin):
    list_display = ('seqinfo', 'cooladminsubmission', 'qc_metrics', 'experiment_type', 'date_last_modified', 'tenx_pipeline_status','path_to_websummary','random_string_link')


@admin.register(TenxqcInfo)
class TenxQCInfoAdmin(admin.ModelAdmin):
    list_display = ('pk','annotated_cells','cellranger_atac_version','cells_detected')


@admin.register(scRNAqcInfo)
class ScRnaQcInfoAdmin(admin.ModelAdmin):
    list_display = ('pk','estimated_number_of_cells','mean_reads_per_cell','median_genes_per_cell')
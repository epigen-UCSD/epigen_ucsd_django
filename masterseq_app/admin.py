from django.contrib import admin
from .models import ProtocalInfo, SeqMachineInfo, GenomeInfo, SampleInfo, SeqInfo, SeqBioInfo, LibraryInfo

# Register your models here.


class GenomeInfoAdmin(admin.ModelAdmin):
    list_display = ('species', 'genome_name')


admin.site.register(GenomeInfo, GenomeInfoAdmin)


class SeqMachineInfoAdmin(admin.ModelAdmin):
    list_display = ('sequencing_core', 'machine_name')


admin.site.register(SeqMachineInfo, SeqMachineInfoAdmin)


class ProtocalInfoAdmin(admin.ModelAdmin):
    list_display = ('experiment_type', 'protocal_name')


admin.site.register(ProtocalInfo, ProtocalInfoAdmin)


@admin.register(SampleInfo)
class SampleInfoAdmin(admin.ModelAdmin):
    list_display = ('sample_id', 'sample_type', 'service_requested', 'group')


@admin.register(SeqInfo)
class SeqInfoAdmin(admin.ModelAdmin):
    list_display = ('seq_id', 'total_reads', 'machine')


@admin.register(LibraryInfo)
class LibraryInfoAdmin(admin.ModelAdmin):
    list_display = ('library_id', 'library_description', 'sampleinfo', 'experiment_type','team_member_initails')

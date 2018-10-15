from django.contrib import admin
from .models import ProtocalInfo,SequencingMachineInfo,GenomeInfo

# Register your models here.
class GenomeInfoAdmin(admin.ModelAdmin):
	list_display = ('species','genome_name')

admin.site.register(GenomeInfo,GenomeInfoAdmin)

class SequencingMachineInfoAdmin(admin.ModelAdmin):
	list_display = ('sequencing_core','machine_name')

admin.site.register(SequencingMachineInfo,SequencingMachineInfoAdmin)

class ProtocalInfoAdmin(admin.ModelAdmin):
	list_display = ('experiment_type','protocal_name')

admin.site.register(ProtocalInfo,ProtocalInfoAdmin)

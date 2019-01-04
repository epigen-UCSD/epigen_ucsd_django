from django.contrib import admin
from .models import ProtocalInfo,SeqMachineInfo,GenomeInfo

# Register your models here.
class GenomeInfoAdmin(admin.ModelAdmin):
	list_display = ('species','genome_name')

admin.site.register(GenomeInfo,GenomeInfoAdmin)

class SeqMachineInfoAdmin(admin.ModelAdmin):
	list_display = ('sequencing_core','machine_name')

admin.site.register(SeqMachineInfo,SeqMachineInfoAdmin)

class ProtocalInfoAdmin(admin.ModelAdmin):
	list_display = ('experiment_type','protocal_name')

admin.site.register(ProtocalInfo,ProtocalInfoAdmin)


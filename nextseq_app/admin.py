from django.contrib import admin
from .models import Barcode, RunInfo, SamplesInRun

class BarcodeAdmin(admin.ModelAdmin):
	list_display = ('indexid','indexseq')

admin.site.register(Barcode,BarcodeAdmin)

class SamplesInRunInline(admin.TabularInline):
	model = SamplesInRun
	extra = 3

class RunInfoAdmin(admin.ModelAdmin):
	list_display = ('Flowcell_ID','operator','date','read_type','read_length')
	inlines = [SamplesInRunInline]

admin.site.register(RunInfo,RunInfoAdmin)

class SamplesInRunAdmin(admin.ModelAdmin):
	list_display = ('singlerun','Library_ID','i7index','i5index')


admin.site.register(SamplesInRun,SamplesInRunAdmin)

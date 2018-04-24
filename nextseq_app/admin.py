from django.contrib import admin
from .models import Barcode, RunInfo, SamplesInRun

class BarcodeAdmin(admin.ModelAdmin):
	list_display = ('indexid','indexseq')

admin.site.register(Barcode,BarcodeAdmin)

class SamplesInRunInline(admin.TabularInline):
	model = SamplesInRun
	extra = 3

class RunInfoAdmin(admin.ModelAdmin):
	list_display = ('runid','operator','date','is_pe','reads_length')
	inlines = [SamplesInRunInline]

admin.site.register(RunInfo,RunInfoAdmin)

class SamplesInRunAdmin(admin.ModelAdmin):
	list_display = ('singlerun','sampleid','i7index','i5index')


admin.site.register(SamplesInRun,SamplesInRunAdmin)

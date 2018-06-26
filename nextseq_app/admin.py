from django.contrib import admin
from .models import Barcode, RunInfo, LibrariesInRun

class BarcodeAdmin(admin.ModelAdmin):
	list_display = ('indexid','indexseq')

admin.site.register(Barcode,BarcodeAdmin)

class LibrariesInRunInline(admin.TabularInline):
	model = LibrariesInRun
	extra = 3

class RunInfoAdmin(admin.ModelAdmin):
	list_display = ('Flowcell_ID','operator','date','read_type','read_length')
	inlines = [LibrariesInRunInline]

admin.site.register(RunInfo,RunInfoAdmin)

class LibrariesInRunAdmin(admin.ModelAdmin):
	list_display = ('singlerun','Library_ID','i7index','i5index')


admin.site.register(LibrariesInRun,LibrariesInRunAdmin)

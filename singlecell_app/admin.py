from django.contrib import admin
from .models import CoolAdminSubmission
# Register your models here.

@admin.register(CoolAdminSubmission)
class SCAdmin(admin.ModelAdmin):
    list_display = ('seqinfo', 'pipeline_version','species', 'date_submitted', 'date_modified')
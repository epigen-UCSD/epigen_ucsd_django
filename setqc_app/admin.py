from django.contrib import admin
from .models import LibrariesSetQC, LibraryInSet

# Register your models here.


@admin.register(LibrariesSetQC)
class SetQCAdmin(admin.ModelAdmin):
    list_display = ('set_id', 'set_name', 'experiment_type')

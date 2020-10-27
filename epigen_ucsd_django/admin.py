from django.contrib import admin

# Register your models here.
from .models import CollaboratorPersonInfo

# Register your models here.


@admin.register(CollaboratorPersonInfo)
class coolabsAdmin(admin.ModelAdmin):
    list_display = ('person_id', 'email', 'group', 'index', 'role')

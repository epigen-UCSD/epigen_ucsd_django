from django.contrib import admin
from collaborator_app.models import ServiceInfo
# Register your models here.


@admin.register(ServiceInfo)
class ServiceInfo(admin.ModelAdmin):
    list_display = ('service_name', 'uc_rate', 'nonuc_rate',
                    'industry_rate', 'rate_unit', 'description_brief', 'description')

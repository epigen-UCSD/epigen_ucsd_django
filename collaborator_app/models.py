from django.db import models
from django.contrib.auth.models import User, Group
from epigen_ucsd_django.models import CollaboratorPersonInfo
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class ServiceInfo(models.Model):
    service_name = models.CharField(max_length=100,unique=True)
    uc_rate = models.FloatField(blank=True, null=True)
    nonuc_rate = models.FloatField(blank=True, null=True)
    industry_rate = models.FloatField(blank=True, null=True)
    rate_unit = models.CharField(max_length=50)
    description_brief = models.TextField(blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    #start_date =  models.DateField(blank=True, null=True)
    #end_date =  models.DateField(blank=True, null=True)

    def __str__(self):
        return self.service_name


class ServiceRequest(models.Model):
    service_request_id = models.CharField(max_length=100,unique=True,blank=True, null=True)
    #quote_number= models.CharField('quote number', max_length=100,unique=True,blank=True, null=True)
    quote_number = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    quote_amount = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    quote_pdf = ArrayField(models.BooleanField(), blank=True, null=True)
    #service_request = models.ManyToManyField(ServiceRequest)
    # group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
    # research_contact = models.ForeignKey(CollaboratorPersonInfo, on_delete=models.CASCADE, blank=True, null=True)
    # research_contact_email = models.CharField(max_length=100, blank=True, null=True)
    group = models.CharField('PI',max_length=200,blank=True, null=True)
    institute_choice = (('uc', 'uc'), ('non_uc', 'non_uc'),('industry', 'industry'))
    institute = models.CharField(max_length=50, choices=institute_choice,blank=True, null=True)
    research_contact = models.CharField(max_length=200,blank=True, null=True)
    research_contact_email = models.CharField(max_length=200,blank=True, null=True)
    date =  models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=50, blank=True, null=True)
 
class ServiceRequestItem(models.Model):
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceInfo, on_delete=models.CASCADE)
    quantity = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)

class UploadQuotePdf(models.Model):
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceInfo, on_delete=models.CASCADE)
    quantity = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
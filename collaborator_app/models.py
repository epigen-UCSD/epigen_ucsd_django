from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.

class ServiceInfo(models.Model):
    service_name = models.CharField(max_length=100,unique=True)
    uc_rate = models.FloatField(blank=True, null=True)
    nonuc_rate = models.FloatField(blank=True, null=True)
    rate_unit = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.service_name

class Request(models.Model):
    quote_number= models.CharField('quote number', max_length=100,unique=True,blank=True, null=True)
    #service_request = models.ManyToManyField(ServiceRequest)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
    date =  models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)

class ServiceRequest(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceInfo, on_delete=models.CASCADE)
    quantity = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
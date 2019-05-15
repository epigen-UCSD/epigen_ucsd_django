from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

choice_for_roles = (
	('PI','PI'),
	('other','other'),
	)

class CollaboratorPersonInfo(models.Model):
	person_id = models.ForeignKey(User, on_delete=models.CASCADE)
	cell_phone = models.CharField('phone',max_length=200,blank=True,null=True)
	email = models.EmailField(max_length=254,blank=True,null=True)
	#phone = PhoneNumberField(null=True, blank=True)
	fiscal_index = models.CharField(max_length=200,blank=True,null=True)
	role_choice = choice_for_roles
	role = models.CharField(max_length=200,choices=role_choice)
	notes = models.TextField(blank=True)

class Person_Index(models.Model):
	index_name = models.CharField(max_length=200,blank=True,null=True)
	person = models.ForeignKey(CollaboratorPersonInfo, on_delete=models.CASCADE,blank=True,null=True)
	class Meta:
		unique_together = ('index_name','person')
		
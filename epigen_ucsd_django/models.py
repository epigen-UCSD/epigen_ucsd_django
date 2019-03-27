from django.db import models
from django.contrib.auth.models import User

choice_for_roles = (
	('PI','PI'),
	('Fiscal','Fiscal'),
	('Research','Research'),
	('PI&Research','PI&Research'),
	('PI&Fiscal','PI&Fiscal'),
	('Research&Fiscal','Research&Fiscal'),
	('PI&Research&Fiscal','PI&Research&Fiscal'),
	('other','other'),
	)

class CollaboratorPersonInfo(models.Model):
	person_id = models.ForeignKey(User, on_delete=models.CASCADE)
	cell_phone = models.CharField(max_length=200,blank=True,null=True)
	fiscal_index = models.CharField(max_length=200,blank=True,null=True)
	role_choice = choice_for_roles
	role = models.CharField(max_length=200,choices=role_choice)

class Person_Index(models.Model):
	index_name = models.CharField(max_length=200,blank=True,null=True)
	person = models.ForeignKey(CollaboratorPersonInfo, on_delete=models.CASCADE)
	class Meta:
		unique_together = ('index_name','person')

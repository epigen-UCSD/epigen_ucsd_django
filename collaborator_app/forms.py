from django import forms
from .models import ServiceInfo,ServiceRequest,ServiceRequestItem

class ServiceRequestItemCreationForm(forms.ModelForm):
    class Meta:
        model = ServiceRequestItem
        fields = ['service', 'quantity']
class ServiceRequestCreationForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'cols': 60, 'rows': 3}),
        }
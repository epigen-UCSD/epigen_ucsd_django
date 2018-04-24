from django.conf.urls import url
from nextseq_app import views

urlpatterns = [
    url(r'^$', views.index,name='index') 
]

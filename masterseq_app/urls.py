from django.conf.urls import url
from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'masterseq_app'
urlpatterns = [

	path('index/', TemplateView.as_view(template_name="masterseq_app/base.html"), name='index'),
    path('sample/adds/', views.SampleCreateView, name='sample_add'),
    path('library/adds/', views.LibraryCreateView, name='library_add'),


]
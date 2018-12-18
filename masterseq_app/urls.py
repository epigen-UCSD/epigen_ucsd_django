from django.conf.urls import url
from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'masterseq_app'
urlpatterns = [

    path('index/', views.IndexView, name='index'),
    path('samples/',views.SampleDataView, name='samples_display'),
    path('libs/',views.LibDataView, name='libs_display'),
    path('seqs/',views.SeqDataView, name='seqs_display'),
    # path('sample/adds/', views.SampleCreateView, name='sample_add'),
    # path('library/adds/', views.LibraryCreateView, name='library_add'),
    # path('seq/adds/', views.SeqCreateView, name='seq_add'),
    # path('ajax/load-protocals/', views.load_protocals, name='ajax_load_protocals'),
    path('samples/adds/', views.SamplesCreateView, name='samples_add'),
    path('libraries/adds/', views.LibrariesCreateView, name='libraries_add'),
    path('seqs/adds/', views.SeqsCreateView, name='seqs_add'),
    path('sample/<int:pk>/delete/', views.SampleDeleteView, name='sample_delete'),
    path('lib/<int:pk>/delete/', views.LibDeleteView, name='lib_delete'),
    path('seq/<int:pk>/delete/', views.SeqDeleteView, name='seq_delete'),
    #path('seqs/adds/confirm', views.SeqsCreateConfirmView, name='seqs_add_confirm'),
    #path('ajaxtest/', TemplateView.as_view(template_name="masterseq_app/ajaxtest.html"), name='ajaxtest'),

]
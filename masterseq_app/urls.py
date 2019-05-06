from django.conf.urls import url
from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'masterseq_app'
urlpatterns = [
    path('index/', views.IndexView, name='index'),
    path('mymeta/', TemplateView.as_view(template_name="masterseq_app/metadata_user.html"), name='user_metadata'),
    path('samples/',views.SampleDataView, name='samples_display'),
    path('libs/',views.LibDataView, name='libs_display'),
    path('seqs/',views.SeqDataView, name='seqs_display'),
    path('usersamples/',views.UserSampleDataView, name='user_samples_display'),
    path('userlibs/',views.UserLibDataView, name='user_libs_display'),
    path('userseqs/',views.UserSeqDataView, name='user_seqs_display'),
    # path('sample/adds/', views.SampleCreateView, name='sample_add'),
    # path('library/adds/', views.LibraryCreateView, name='library_add'),
    # path('seq/adds/', views.SeqCreateView, name='seq_add'),
    path('ajax/load-protocals/', views.load_protocals, name='ajax_load_protocals'),
    path('ajax/load-samples/', views.load_samples, name='ajax_load_samples'),
    path('ajax/load-libs/', views.load_libs, name='ajax_load_libs'),
    path('samples/adds/', views.SamplesCreateView, name='samples_add'),
    path('libraries/adds/', views.LibrariesCreateView, name='libraries_add'),
    path('seqs/adds/', views.SeqsCreateView, name='seqs_add'),
    path('sample/<int:pk>/delete/', views.SampleDeleteView, name='sample_delete'),
    path('lib/<int:pk>/delete/', views.LibDeleteView, name='lib_delete'),
    path('seq/<int:pk>/delete/', views.SeqDeleteView, name='seq_delete'),
    path('sample/<int:pk>/update/', views.SampleUpdateView, name='sample_update'),
    path('lib/<int:pk>/update/', views.LibUpdateView, name='lib_update'),
    path('seq/<int:pk>/update/', views.SeqUpdateView, name='seq_update'),
    path('sample/<int:pk>/', views.SampleDetailView, name='sample_detail'),
    path('lib/<int:pk>/', views.LibDetailView, name='lib_detail'),
    path('seq/<int:pk>/', views.SeqDetailView, name='seq_detail'),
    path('seq/<slug:seqid>/', views.SeqDetail2View, name='seq_detail_fromseqid'),
    #path('seqs/adds/confirm', views.SeqsCreateConfirmView, name='seqs_add_confirm'),
    #path('ajaxtest/', TemplateView.as_view(template_name="masterseq_app/ajaxtest.html"), name='ajaxtest'),
    path('savemymetadatatoexcel/', views.SaveMyMetaDataExcel, name='user_metadata_save_excel'),
    path('saveallmetadatatoexcel/', views.SaveAllMetaDataExcel, name='all_metadata_save_excel'),
    path('samplescollabs/adds/', views.SamplesCollabsCreateView, name='samplescollabs_add'),
    path('ajax/load-researchcontact/', views.load_researchcontact, name='ajax_load_researchcontact'),
    path('ajax/load-fiscalindex/', views.load_fiscalindex, name='ajax_load_fiscalindex'),



]
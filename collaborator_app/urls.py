from django.conf.urls import url
from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'collaborator_app'
urlpatterns = [
    path('metadata/mymeta/', TemplateView.as_view(template_name="collaborator_app/collab_metadata_user.html"), name='user_metadata'),
    path('metadata/usersamples/',views.UserSampleDataView, name='user_samples_display'),
    path('metadata/userlibs/',views.UserLibDataView, name='user_libs_display'),
    path('metadata/userseqs/',views.UserSeqDataView, name='user_seqs_display'),    
    path('setqc/mysets/', TemplateView.as_view(template_name="collaborator_app/collab_setqc_user.html"), name='usersetqcs'),
    path('setqc/<int:setqc_pk>/getmynotes/',views.CollaboratorGetNotesView, name='setqc_getnotes'),
    #path('userscseqs', views.UserSingleCellSeqs, name='user_scseqs_display'),
    path('myprofile/',views.UserProfileView, name='user_profile'),  



    path('setqc/usersetqcs/',views.UserSetqcView, name='user_setqcs_display'),

    path('changepassword/', views.collab_change_password, name='collab_change_password'),
    path('setqc/myreports/', views.CollaboratorSetQCView, name='collaboratorsetqcs'),
    path('setqc//<int:setqc_pk>/details/',views.CollaboratorSetQCDetailView, name='setqc_collaboratordetail'),
    path('setqc/<int:setqc_pk>/getnotes/',views.CollaboratorGetNotesView, name='setqc_collaboratorgetnotes'),
    path('mysamples/', views.CollaboratorSampleView, name='collab_samples'),
    path('mysamples_com/', views.CollaboratorSampleComView, name='collab_samples_compare'),

    path('feeforservice/servicerequest/', views.ServiceRequestListView, name='collab_servicerequest_list'),
    path('feeforservice/servicerequest_add/', views.ServiceRequestCreateView, name='collab_servicerequest_add'),

]
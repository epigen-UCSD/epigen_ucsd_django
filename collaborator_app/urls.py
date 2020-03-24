from django.conf.urls import url
from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'collaborator_app'
urlpatterns = [
    path('mymeta/', TemplateView.as_view(template_name="collaborator_app/collab_metadata_user.html"), name='user_metadata'),
    path('usersamples/',views.UserSampleDataView, name='user_samples_display'),
    path('userlibs/',views.UserLibDataView, name='user_libs_display'),
    path('userseqs/',views.UserSeqDataView, name='user_seqs_display'),    
    path('mysets/', TemplateView.as_view(template_name="collaborator_app/collab_setqc_user.html"), name='usersetqcs'),
    path('<int:setqc_pk>/getmynotes/',views.CollaboratorGetNotesView, name='setqc_getnotes'),
    path('myprofile/',views.UserProfileView, name='user_profile'),  


    path('usersetqcs/',views.UserSetqcView, name='user_setqcs_display'),

    path('changepassword/', views.collab_change_password, name='collab_change_password'),
    path('myreports/', views.CollaboratorSetQCView, name='collaboratorsetqcs'),
    path('<int:setqc_pk>/details/',views.CollaboratorSetQCDetailView, name='setqc_collaboratordetail'),
    path('<int:setqc_pk>/getnotes/',views.CollaboratorGetNotesView, name='setqc_collaboratorgetnotes'),
    path('mysamples/', views.CollaboratorSampleView, name='collab_samples'),
    path('mysamples_com/', views.CollaboratorSampleComView, name='collab_samples_compare'),

]
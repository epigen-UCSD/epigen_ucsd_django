from django.conf.urls import url
from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'collaborator_app'
urlpatterns = [
    path('changepassword/', views.collab_change_password, name='collab_change_password'),
    path('myreports/', views.CollaboratorSetQCView, name='collaboratorsetqcs'),
    path('<int:setqc_pk>/details/',views.CollaboratorSetQCDetailView, name='setqc_collaboratordetail'),
    path('<int:setqc_pk>/getnotes/',views.CollaboratorGetNotesView, name='setqc_collaboratorgetnotes'),
    path('mysamples/', views.CollaboratorSampleView, name='collab_samples'),

]
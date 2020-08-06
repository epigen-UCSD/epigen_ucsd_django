from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'setqc_app'
urlpatterns = [

    path('', views.UserSetQCView, name='index'),
    path('mysets/', views.UserSetQCView, name='usersetqcs'),
    path('allsets/', views.AllSetQCView, name='allsetqcs'),
    path('adds/', views.SetQCCreateView, name='setqc_add'),
    path('<int:setqc_pk>/labelgenomeadds/', views.SetQCgenomelabelCreateView, name='libraylabelgenome_add'),
    path('<int:setqc_pk>/labelgenomeupdates/', views.SetQCgenomelabelUpdateView, name='libraylabelgenome_update'),
    path('<int:setqc_pk>/delete/', views.SetQCDeleteView, name='setqc_delete'),
    path('<int:setqc_pk>/update/',views.SetQCUpdateView, name='setqc_update'),
    path('<int:setqc_pk>/getmynotes/',views.GetNotesView, name='setqc_getnotes'),
    path('<int:setqc_pk>/runsetqc/',views.RunSetQC, name='runsetqc'),
    path('<int:setqc_pk>/runsetqc2/',views.RunSetQC2, name='runsetqc2'),
    path('<int:setqc_pk>/',views.SetQCDetailView, name='setqc_detail'),
    path('ajax/load-users/', views.load_users, name='ajax_load_users'),
    path('<int:setqc_pk>/<str:outputname>/web_summary.html', views.tenx_output, name='10xATACoutput'),
    #path('encodesetadd/', views.EncodeSetQCCreateView, name='encode_setqc_add'),

]

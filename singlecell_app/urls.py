from django.urls import path, include
from . import views

app_name = 'singlecell_app'
urlpatterns = [
    path('mysclibs', views.scIndex, name='scindex'),
    path('allsclibs', views.AllScLibs, name='allsclibs'),
    path('AllSeqs', views.AllSeqs, name='allseqs'),
    path('MySeqs', views.MySeqs, name='myseqs'),
    path('Ajax/submitSN/', views.SubmitToCoolAdmin, name='submitcooladmin'),
    path('Ajax/submit/', views.SubmitSingleCell, name='submitsinglecell'),
    path('libs',include('masterseq_app.urls')),
]
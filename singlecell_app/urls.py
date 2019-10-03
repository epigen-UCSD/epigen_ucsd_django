from django.urls import path
from . import views

app_name = 'singlecell_app'
urlpatterns = [
    path('mysclibs', views.scIndex, name='scindex'),
    path('allsclibs', views.AllScLibs, name='allsclibs'),
    path('AllSeqs', views.AllSeqs, name='allseqs'),
    path('MySeqs', views.MySeqs, name='myseqs'),
    
]
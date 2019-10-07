from django.urls import path, include
from . import views

app_name = 'singlecell_app'
urlpatterns = [
    path('mysclibs', views.scIndex, name='scindex'),
    path('allsclibs', views.AllScLibs, name='allsclibs'),
    path('AllSeqs', views.AllSeqs, name='allseqs'),
    path('MySeqs', views.MySeqs, name='myseqs'),
    path('libs',include('masterseq_app.urls')),
    path('Submit', views.SubmitToTenX, name='submittotenx')
]
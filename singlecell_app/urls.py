from django.urls import path, include
from . import views

app_name = 'singlecell_app'
urlpatterns = [
    path('AllSeqs', views.AllSeqs, name='allseqs'),
    path('MySeqs', views.MySeqs, name='myseqs'),
    path('EditCoolAdmin/<str:seqinfo>', views.EditCoolAdminSubmission, name='editcooladmin'),
    path('Ajax/SubmitCA/',views.SubmitToCoolAdmin, name='submitcooladmin'),
    path('Ajax/Submit/', views.SubmitSingleCell, name='submitsinglecell'),
    path('libs',include('masterseq_app.urls')),
]
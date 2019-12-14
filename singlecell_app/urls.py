from django.urls import path, include
from . import views

app_name = 'singlecell_app'
urlpatterns = [
    path('AllSeqs', views.AllSeqs, name='allseqs'),
    path('all_singlecell_data/', views.AllSingleCellData, name='all_singlecell_data'),
    path('user_singlecell_data/', views.UserSingleCellData, name='user_singlecell_data'),
    path('MySeqs', views.MySeqs, name='myseqs'),
    path('EditCoolAdmin/<str:seqinfo>', views.EditCoolAdminSubmission, name='editcooladmin'),
    path('ajax/submitcooladmin/',views.SubmitToCoolAdmin, name='submitcooladmin'),
    path('ajax/submit/', views.SubmitSingleCell, name='submitsinglecell'),
    path('libs',include('masterseq_app.urls')),
]
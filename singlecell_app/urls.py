from django.urls import path, include
from . import views

app_name = 'singlecell_app'
urlpatterns = [
    path('AllSeqs', views.AllSeqs, name='allseqs'),
    path('MySeqs', views.MySeqs, name='myseqs'),
    path('all_singlecell_data/', views.AllSingleCellData, name='all_singlecell_data'),
    path('user_singlecell_data/', views.UserSingleCellData, name='user_singlecell_data'),
    path('EditCoolAdmin/<str:seqinfo>', views.edit_cooladmin_sub, name='editcooladmin'),
    path('ajax/submitcooladmin/',views.submit_cooladmin, name='submitcooladmin'),
    path('ajax/submit/', views.submit_singlecell, name='submitsinglecell'),
]
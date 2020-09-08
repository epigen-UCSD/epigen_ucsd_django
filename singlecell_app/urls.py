from django.urls import path, include
from . import views

app_name = 'singlecell_app'
urlpatterns = [
    path('AllSeqs', views.AllSeqs, name='allseqs'),
    path('MySeqs', views.MySeqs, name='myseqs'),
    path('all_singlecell_data/', views.AllSingleCellData, name='all_singlecell_data'),
    path('user_singlecell_data/', views.UserSingleCellData, name='user_singlecell_data'),
    path('all_10xATAC_QC_data/', views.All10xAtacQcData, name='all_10xATAC_QC_data'),
    path('user_10xATAC_QC_data/', views.User10xAtacQcData, name='user_10xATAC_QC_data'),
    path('all_10xRNA_QC_data/', views.All10xRnaQcData, name='all_10xRNA_QC_data'),
    path('user_10xRNA_QC_data/', views.User10xRnaQcData, name='user_10xRNA_QC_data'),
    path('EditCoolAdmin/<str:seqinfo>', views.edit_cooladmin_sub, name='editcooladmin'),
    path('ajax/submitcooladmin/',views.submit_cooladmin, name='submitcooladmin'),
    path('ajax/submit/', views.submit_singlecell, name='submitsinglecell'),
    path('ajax/generate_link', views.generate_tenx_link, name='generate_link'),
    path('websummary/<str:seq_id>',views.view_websummary,name="view_websummart"),

]
from django.conf.urls import url
from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'manager_app'
urlpatterns = [
    path('collab_list/', views.CollaboratorListView, name='collab_list'),
    #path('collab_add/', views.CollaboratorCreateView, name='collab_add'),
    path('collab_group_account_add/', views.GroupAccountCreateView, name='group_account_add'),
    #path('index_add/', views.IndexCreateView, name='index_add'),
    path('collabinfo_add/', views.CollabInfoAddView, name='collabinfo_add'),
    path('ajax/load-groups/', views.load_groups, name='ajax_load_groups'),
    path('ajax/group_add/', views.AjaxGroupCreateView, name='ajax_group_add'),
    path('ajax/load-collabs/', views.load_collabs, name='ajax_load_collabs'),


]
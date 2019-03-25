from django.conf.urls import url
from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'manager_app'
urlpatterns = [
    path('collab_list/', views.CollaboratorListView, name='collab_list'),

]
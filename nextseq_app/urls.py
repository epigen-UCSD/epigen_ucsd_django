from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'nextseq_app'
urlpatterns = [
    url(r'^$', views.index,name='index'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
]

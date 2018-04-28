from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'nextseq_app'
urlpatterns = [
    #path('', views.IndexView.as_view(),name='index'),
    path('', views.IndexView,name='index'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),


]

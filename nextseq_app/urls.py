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
    #path('<int:pk>/', views.RunDetailView.as_view(), name='rundetail'),
    path('<int:pk>/', views.RunDetailView.as_view(), name='rundetail'),
    path('add/', views.RunCreateView2.as_view(), name='run_add'),
    path('<int:pk>/update/', views.RunUpdateView.as_view(), name='run_update'),
    path('<int:pk>/delete/', views.RunDeleteView.as_view(), name='run_delete'),


]

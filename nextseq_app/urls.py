from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'nextseq_app'
urlpatterns = [

    path('', views.IndexView, name='index'),
    path('myruns/', views.IndexView, name='userruns'),
    path('mysamples/', views.UserSamplesView, name='usersamples'),
    path('allruns/', views.HomeView.as_view(), name='allruns'),
    path('allsamples/', views.AllSamplesView, name='allsamples'),
    #path('register/', views.UserRegisterView.as_view(), name='register'),
    #path('login/', views.UserLoginView.as_view(), name='login'),
    #path('logout/', views.logout_view, name='logout'),
    path('<int:pk>/', views.RunDetailView2.as_view(), name='rundetail'),
    #path('<int:pk>/', views.RunDetailView, name='rundetail'),
    #path('home/<int:pk>/', views.RunDetailViewhome.as_view(), name='rundetailhome'),
    path('adds/', views.RunCreateView4, name='runandsample_add'),
    path('addsinbulky/', views.RunCreateView6, name='runandsample_add_inbulky'),
    path('<slug:username>/<int:run_pk>/update/',
         views.RunUpdateView2, name='run_update'),
    path('<int:run_pk>/delete2/', views.RunDeleteView2, name='run_delete2'),
    path('<int:run_pk>/samplesheetcreate/',
         views.SampleSheetCreateView, name='samplesheet_create'),
    #path('changepassword/', views.change_password, name='change_password'),
    path('<int:run_pk>/demultiplexing/',
         views.DemultiplexingView, name='demultiplexing'),
    path('<int:run_pk>/demultiplexing2/',
         views.DemultiplexingView2, name='demultiplexing2'),

]

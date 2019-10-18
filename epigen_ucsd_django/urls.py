"""epigen_ucsd_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
#from nextseq_app import views
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('nextseq/', include('nextseq_app.urls')),
    path('setqc/', include('setqc_app.urls')),
    path('metadata/', include('masterseq_app.urls')),
    path('manager/', include('manager_app.urls')),
    path('epigen/', include('collaborator_app.urls')),
    path('nextseq/login/', views.UserLoginView.as_view(), name='loginfromnexseq'),
    path('nextseq_app/login/', views.UserLoginView.as_view(),
         name='loginfromnexseq2'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('', views.UserLoginView.as_view(), name='login_from_base'),
    path('logout/', views.logout_view, name='logout'),
    path('changepassword/', views.change_password, name='change_password'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('singlecell/', include('singlecell_app.urls')),
]

if 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns



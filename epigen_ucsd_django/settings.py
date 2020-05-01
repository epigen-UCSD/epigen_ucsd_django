"""
Django settings for epigen_ucsd_django project.

Generated by 'django-admin startproject' using Django 2.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import configparser
import os


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(BASE_DIR,'templates')
static_dir = os.path.join(BASE_DIR, "static")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/
config = configparser.ConfigParser()
config.read('deploy.ini.eg')
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config['django']['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['epigenomics.sdsc.edu', '127.0.0.1']
INTERNAL_IPS = ['127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'nextseq_app',
    'setqc_app',
    'masterseq_app',
    'epigen_ucsd_django',
    'django.contrib.humanize',
    'manager_app',
    'collaborator_app',
    'singlecell_app',
    'debug_toolbar',
    'bootstrap4',
]

if 'extra_app' in dict(config.items('database')).keys():
    INSTALLED_APPS.append(config['database']['EXTRA_APP'])

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'epigen_ucsd_django.middleware.LoginRequiredMiddleware',
    'epigen_ucsd_django.middleware.InternalRequiredMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',


]

if 'extra_middleware' in dict(config.items('database')).keys():
    MIDDLEWARE.append(config['database']['EXTRA_MIDDLEWARE'])

ROOT_URLCONF = 'epigen_ucsd_django.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [template_dir,],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'epigen_ucsd_django.wsgi.application'

STATICFILES_DIRS = [

    static_dir,

]


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
# https://docs.python.org/3/library/configparser.html#rawconfigparser-objects

# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#    }
# }


DATABASES = {
    'default': {
        'ENGINE': config['database']['DATABASE_ENGINE'],
        'NAME': config['database']['DATABASE_NAME'],
        'USER': config['database']['DATABASE_USER'],
        'PASSWORD': config['database']['DATABASE_PASSWORD'],
        'HOST': config['database']['DATABASE_HOST'],
        'PORT': config['database']['DATABASE_PORT'],
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

LOGIN_URL = '/login/'

LOGIN_EXEMPT_URLS = (

    r'register/',
    r'admin/',

)
INTERNAL_EXEMPT_URLS = (
    r'setqc/myreports/',
    r'epigen/',
    r'setqc/(\d+)/details/',
    r'setqc/(\d+)/getnotes/',
    r'logout/',
    r'__debug__/',
    r'admin/',
    r'register/',
    r'changepassword/',

)

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

NEXTSEQAPP_DMPDIR = config['database']['NEXTSEQAPP_DMPDIR']
LIBQC_DIR = config['database']['LIBQC_DIR']
SETQC_DIR = config['database']['SETQC_DIR']
FASTQ_DIR = config['database']['FASTQ_DIR']
TENX_DIR = config['database']['TENX_DIR']
MEDIA_ROOT = config['database']['MEDIA_ROOT']
TENX_WEBSUMMARY = config['snapp']['TENX_WEBSUMMARY']
COOLADMIN_DIR = config['snapp']['COOLADMIN_DIR']
ENCODE_TM_DIR = config['database']['ENCODE_TM_DIR']
SCRNA_DIR = config['snapp']['SCRNA_DIR']
EXPOSED_OUTS_DIR = config['snapp']['EXPOSED_OUTS_DIR']

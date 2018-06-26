# Nextseq app 


## Requirement 

* Python: v3.6.5
* Django: 2.0.4

## Install 

### Install conda envirionment 

``` Shell
 conda create -n ${ENV_NAME}  --file requirement.txt -c defaults -c conda-forge 
```
### Set up database 

``` Shell
# 1. init db
pg_ctl -D /Users/frank/pgsql/data -l logfile start

# 2. start db 
pg_ctl -D /Users/frank/pgsql/data -l logfile start

# 3. create db
createdb nextseqapp

# 4. enter db
psql -d nextseqapp
```

Change user to test 

``` SQL
CREATE DATABASE nextseqapp OWNER test;
ALTER USER test WITH PASSWORD '123456';
```

## Run 
``` Shell
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 
python manage.py createsuperuser
```
### deploy 

``` shell
python manage.py runserver 0.0.0.0:8000
```

### change sqlite3 to postgresql:

1. 
replace:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
with:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

2. remove all __pycache__ folder and migration history

find . -name "__pycache__" | xargs rm -r
find . -name "000*.py" | xargs rm

3.
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser


### import existing barcodes into database:

go to scripts folder:
python barcodeimport.py

### testing account

username: test
password: testdjango

## links 

* Register: [test](http://127.0.0.1:8000/nextseq_app/register/),[deployed](http://epigenomics.sdsc.edu:8000/nextseq_app/register/)
* Login: [test](http://127.0.0.1:8000/nextseq_app/login/),[deployed](http://epigenomics.sdsc.edu:8000/nextseq_app/login/)




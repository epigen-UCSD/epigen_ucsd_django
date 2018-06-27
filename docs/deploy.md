# Deploy #

## set up postgresql

* [server admin](https://www.postgresql.org/docs/10/static/admin.html)
* [nfs harmful](https://www.time-travellers.org/shane/papers/NFS_considered_harmful.html)
* [multiple db in django](https://docs.djangoproject.com/en/2.0/topics/db/multi-db/). Limitation: cross-database relations. 

## change sqlite3 to postgresql:

* split setting: https://code.djangoproject.com/wiki/SplitSettings. Use `.ini` method. 

1. replace:

``` shell
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

```

with:

``` shell
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

```

2. remove all`__pycache__` folder and migration history

`find . -name "__pycache__" | xargs rm -r`
`find . -name "000*.py" | xargs rm`

3. cmds 

``` shell
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### import existing barcodes into database:

copy deploy.ini to folder scritps, 
go to scripts folder:
`python barcodeimport.py`

# Deploy #


## change sqlite3 to postgresql:

1.replace:

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

go to scripts folder:
python barcodeimport.py

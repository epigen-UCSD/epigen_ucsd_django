# Nextseq app 


## Requirement 

* Python: v3.6.5
* Django: 2.2.5

## Install 

### Install conda envirionment 

``` Shell
 conda create -n ${ENV_NAME}  --file requirement.txt -c defaults -c conda-forge 
```
Another option since we did no mantain the requirement.txt
``` Shell
 conda env create -f django.yml
 source activate django
```


### Set up database 

see [here](./docs/db.md)
``` Shell
# 1. init db
pg_ctl -D /Users/frank/pgsql/data -l logfile init

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
Create a deploy.ini file under folder epigen_ucsd_django/, check that file in deploy env to see what should be included. then run the following:
``` Shell
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 
python manage.py createsuperuser
```
### deploy 

see [ here ](./docs/deploy.md)

``` shell
python manage.py runserver 0.0.0.0:8000
```
### testing account

username: test
password: testdjango

## links 

* Register: [test](http://127.0.0.1:8000/nextseq_app/register/),[deployed](http://epigenomics.sdsc.edu:8000/nextseq_app/register/)
* Login: [test](http://127.0.0.1:8000/nextseq_app/login/),[deployed](http://epigenomics.sdsc.edu:8000/nextseq_app/login/)

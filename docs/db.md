# Setup Database #

* `su postgres`
``` Shell
initdb -D /usr/local/pgsql/data
postgres -D /usr/local/pgsql/data >pg_logfile 2>&1 &
pg_ctl start -l logfile #use wrapper
createdb nextseqapp
# enter db
psql -d nextseqapp
```

* stop: `pg_ctl -D /usr/local/pgsql/data/ stop`
* kill; `pkill postgres` or `sudo pkill -u postgres`
* createdb: `createdb django_data`
* check status: `/sbin/service postgresql status`

Change user to test 

## SQL cmd
``` SQL
CREATE DATABASE nextseqapp OWNER test;
ALTER USER test WITH PASSWORD '123456';
```

## psql shell 
* list: `\l`


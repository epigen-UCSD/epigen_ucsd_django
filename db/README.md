# Setup Database #

## cmds
* switch user: `su postgres`
* init: `initdb -D /usr/local/pgsql/data`
* start: `postgres -D /usr/local/pgsql/data >pg_logfile 2>&1 &`  or `pg_ctl start -l logfile #use wrapper`
* createdb: `createdb django_data`
* enter db:`psql -d django_data`
* stop: `pg_ctl -D /usr/local/pgsql/data/ stop`
* kill; `pkill postgres` or `sudo pkill -u postgres`
* createdb: `createdb django_data`
* check status: `/sbin/service postgresql status`
* backup & recover all: `pg_dumpall > outfile` and `psql -f infile postgres`
* backup & recover db: `pg_dump django_data > pg.backup` and `psql -f infile postgres`
* cron: [setup](https://www.saltycrane.com/blog/2008/12/postgres-backup-cron/)

## SQLs
* Change user to test: 
``` SQL
CREATE DATABASE nextseqapp OWNER test;
ALTER USER test WITH PASSWORD '123456';
```
## psql shell 
* list: `\l`

## URL
* [nextseq@dbdiagram.io](https://dbdiagram.io/d/5c3d227619c125001489f837)
* [metadata@dbdiagram.io](https://dbdiagram.io/d/5bb396d8e63c1f0014dab57d)
* [usrs@dbdigram.io](https://dbdiagram.io/d/5c05a310b155a200149def72)
* [FeeForServiceModel](https://dbdiagram.io/d/5e691c144495b02c3b881e6d)

* [CoolAdminModel](https://dbdiagram.io/d/5dc0512fedf08a25543d7eb5)

# Migration Instruction for Special Cases: #

## change group from char to foreign key for SetQC app (existing char group is none, no need to transer data)
* from django.contrib.auth.models import User,Group for setqc_app models.py file
* add group_tm = models.ForeignKey(Group,on_delete=models.CASCADE,blank=True,null=True) to model LibrariesSetQC(models.Model), then run makemigrations and migrate as normal
* remove group = models.CharField(max_length=100,blank=True,null=True) from model LibrariesSetQC(models.Model), then run makemigrations and migrate as normal
* change group_tm to group, then run makemigrations and migrate as normal
* push to master branch
* merge branch 'liyuxin' where the commit message is 'changed group from char to foreign key for SetQC app'


## change group from char to foreign key for Metadata app (existing char group is not none, need to transer data)
* merge branch 'liyuxin' where the commit message is 'changed group from char to foreign key for Metadata app'
* replace 'group = models.ForeignKey(Group,on_delete=models.CASCADE,blank=True,null=True)' with 'group = models.CharField(max_length=100, blank=True, null=True)
    group_tm = models.ForeignKey(Group,on_delete=models.CASCADE,blank=True,null=True)', then run makemigrations and migrate as normal
* run `python scripts/TransferGroupfromChartoFK.py`
* Remove field group from sampleinfo
* rename sampleinfo.group_tm to sampleinfo.group








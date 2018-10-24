# Scripts Folder #

## group user into different groups:

1. go to groupUserscfg file, change the contents as you need. There is already an example in this file, just replace the group name and user name with your real data.

2. run this command to import the groups and its user_set into database:

```shell
python groupUsers.py
```

## update status and dir in run:

```shell
python updateRunStatus.py -s '0' -f 'H5GLYBGX5fff'
```
or

```shell
python updateRunStatus.py -s '0' -d '/Users/180705_AH5GLYBGX5431' -f 'H5GLYBGX5fff'
```

## Save Reads Number to Library:

1. go to readsnumber.tsv file, fill out your reads number for each library, first column is library name, second column is #reads.

2. run this command to save reads numbers into database

```shell
python saveReadsNumber.py -i 'scripts/readsnumber.tsv'
```

## import existed sequencing id in MSeqTS to database:

```shell
python mseqinfoimport.py -i 'scripts/MSeqTS.tsv'
python mseqinfoimport.py -i 'scripts/MSeqTSarchive.tsv'
```

## import existed setQC reports with requested date later than -date in MSQcTS to database:

```shell
python setqcimport.py -i 'scripts/MSQcTS.tsv' -date '2018-07-18'
```
* Note: the libraries in 'Libraries to include' column should be separated by comma. This script can understand grouped-libraries format, but you still need adhere to some rules, like enter in 'JYH_554 - 556, JYH_558 - 560, JYH_570' instead of 'JYH_554 - 556, 558 - 560, 570'. The cells with a date later than '2018-07-18' that cann't be parsed has been corrected manually.

## import existing data to the tables in masterseq app

1. check if member exist, if not, add it through admin. But it is okay to skip this step, if you are fine with setting the team_member_initails to null in database, and moving it to the notes field:
```shell
AVD,JIB,JYH,RMM,XH,XW,DUG,SP,ZC
```
2. clear the data in masterseq app and setqc app
3. makemigrations and migrate:
```shell
python manage.py makemigrations
python manage.py migrate
```
4. go to scripts/ folder, run this command:

```shell
python import_masterseq_data_inial.py
```



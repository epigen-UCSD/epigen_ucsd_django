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
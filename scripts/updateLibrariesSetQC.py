#!/usr/bin/env python
import os
import sys
import django
import argparse
# print(os.path.abspath(__file__))


basedir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(basedir))
sys.path.append(basedir)
sys.path.append(os.path.dirname(basedir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()

from setqc_app.models import LibrariesSetQC


def main():
    # for example: python updateLibrariesSetQC.py -s '0' -id 'Set_168'
    #python updateLibrariesSetQC.py -url '' -v '' -id 'Set_168'
    statuscode = {'-1': 'ClickToSubmit', '0': 'JobSubmitted',
                  '1': 'JobStarted', '2': 'Done', '3': 'Error', '4': 'Warning'}
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', choices=['-1', '0', '1', '2', '3', '4'],
                        help='-1: ClickToSubmit 0:JobSubmitted 1:JobStarted 2:Done 3:Error 4:Warning')
    parser.add_argument('-id', help='Set_ID')
    parser.add_argument('-url', help='url of report')
    parser.add_argument('-v', help='version of runsetqc script')
    
    thissetid = parser.parse_args().id
    thisstatus = ''
    thisurl = ''
    thisversion = ''

    try:
        thisstatus = parser.parse_args().s
        thisurl = parser.parse_args().url
        thisversion = parser.parse_args().v
    except:
        pass
    
    # would not update 'Last Modified' column in this way
    # LibrariesSetQC.objects.filter(setID=thissetid).update(status=statuscode[thisstatus])
    obj = LibrariesSetQC.objects.get(set_id=thissetid)
    if thisstatus:
        obj.status = statuscode[thisstatus]
    if thisurl:
        obj.url = thisurl
    if thisversion:
        obj.version = thisversion
    obj.save()


if __name__ == '__main__':
    main()

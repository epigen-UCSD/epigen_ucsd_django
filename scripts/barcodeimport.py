#!/usr/bin/env python
# Time-stamp: <2018-07-03 09:01:48>

import os
import sys
import django
os.chdir("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()
from nextseq_app.models import Barcode

def getArgs():
        import argparse
        parser = argparse.ArgumentParser(description='Import barcodes script.')
        parser.add_argument('-b','--barcode_file', dest='barcode_file', 
                    help='input barcode file  (csv format)')

        args = parser.parse_args()
        return args.barcode_file

def main():
        with io.open('./data/nextseq_app/barcodes/JYH_2018-07-02_barcodes.csv','r',encoding='utf-8') as f: lines = f.read().splitlines()
        indexes = {l.replace(u'\ufeff','').split(',')[0]:l.replace(u'\ufeff','').split(',')[1]for l in lines}
        for k,v in indexes.items(): obj,created=Barcode.objects.get_or_create(indexid=k, indexseq=v)

if __name__ == '__main__':
	main()




#!/usr/bin/env python
# Time-stamp: <2019-01-17 12:40:00>

import os
import sys
import django
import io

os.chdir("../")
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()
from nextseq_app.models import Barcode


def getArgs():
    import argparse
    parser = argparse.ArgumentParser(
        description='Import barcodes script for 10xATAC.')
    parser.add_argument('-b', '--barcode_file', dest='barcode_file',
                        help='input barcode file  (csv format, basedir is ../scripts)')
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    return args.barcode_file


def main():
    fn = getArgs()
    with io.open(fn, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()
    indexes = [l.replace(u'\ufeff', '').split(',')[0] for l in lines]

    for nm in indexes:
        obj, created = Barcode.objects.get_or_create(
            indexid=nm, indexseq=nm, kit='TA')


if __name__ == '__main__':
    main()

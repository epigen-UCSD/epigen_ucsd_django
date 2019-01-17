#!/usr/bin/env python
# Time-stamp: <2019-01-17 12:04:22>

import os
import sys
import django
import io
import itertools


# os.chdir("../")
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epigen_ucsd_django.settings")
django.setup()
from nextseq_app.models import Barcode


def main():
    stuff = [a for a in range(1, 9)]
    all_bns = []
    for L in stuff:
        for subset in itertools.combinations(stuff, L):
            nm = ','.join([str(i) for i in subset])
            obj, created = Barcode.objects.get_or_create(
                indexid=nm, indexseq=nm, kit='S2')


if __name__ == '__main__':
    main()

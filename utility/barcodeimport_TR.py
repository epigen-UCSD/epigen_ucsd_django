#!/usr/bin/env python

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

barcodes_set = ['SI-GA-A1','SI-GA-A2','SI-GA-A3','SI-GA-A4','SI-GA-A5','SI-GA-A6','SI-GA-A7','SI-GA-A8','SI-GA-A9','SI-GA-A10','SI-GA-A11','SI-GA-A12','SI-GA-B1','SI-GA-B2','SI-GA-B3','SI-GA-B4','SI-GA-B5','SI-GA-B6','SI-GA-B7','SI-GA-B8','SI-GA-B9','SI-GA-B10','SI-GA-B11','SI-GA-B12','SI-GA-C1','SI-GA-C2','SI-GA-C3','SI-GA-C4','SI-GA-C5','SI-GA-C6','SI-GA-C7','SI-GA-C8','SI-GA-C9','SI-GA-C10','SI-GA-C11','SI-GA-C12','SI-GA-D1','SI-GA-D2','SI-GA-D3','SI-GA-D4','SI-GA-D5','SI-GA-D6','SI-GA-D7','SI-GA-D8','SI-GA-D9','SI-GA-D10','SI-GA-D11','SI-GA-D12','SI-GA-E1','SI-GA-E2','SI-GA-E3','SI-GA-E4','SI-GA-E5','SI-GA-E6','SI-GA-E7','SI-GA-E8','SI-GA-E9','SI-GA-E10','SI-GA-E11','SI-GA-E12','SI-GA-F1','SI-GA-F2','SI-GA-F3','SI-GA-F4','SI-GA-F5','SI-GA-F6','SI-GA-F7','SI-GA-F8','SI-GA-F9','SI-GA-F10','SI-GA-F11','SI-GA-F12','SI-GA-G1','SI-GA-G2','SI-GA-G3','SI-GA-G4','SI-GA-G5','SI-GA-G6','SI-GA-G7','SI-GA-G8','SI-GA-G9','SI-GA-G10','SI-GA-G11','SI-GA-G12','SI-GA-H1','SI-GA-H2','SI-GA-H3','SI-GA-H4','SI-GA-H5','SI-GA-H6','SI-GA-H7','SI-GA-H8','SI-GA-H9','SI-GA-H10','SI-GA-H11','SI-GA-H12']


def main():

    for nm in barcodes_set:
        obj, created = Barcode.objects.get_or_create(
            indexid=nm, indexseq=nm, kit='TR')


if __name__ == '__main__':
    main()

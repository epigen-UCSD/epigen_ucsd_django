#!/usr/bin/env python
import argparse
import os


def genTAbarcodeDic(ta_barcode_file):
    """
    generate barcode_dic with `SI_TT_XX` as key and i7,i5_a,i5_b(nextseq) as values
    https://support.10xgenomics.com/spatial-gene-expression/software/pipelines/latest/using/bcl2fastq-direct
    """
    ta_barcode_dic = {}
    # ta_barcode_file = os.path.join(
    #    'data', 'nextseq_app', 'barcodes', "chromium-shared-sample-indexes-plate.csv")
    line_num = 0
    with open(ta_barcode_file) as f:
        for line in f:
            if(line_num > 0):
                tmpstr = line.rstrip().split(',')
                ta_barcode_dic[tmpstr[0]] = tmpstr[1:]
            line_num += 1
    return(ta_barcode_dic)


def argsHandler():
    parser = argparse.ArgumentParser(
        description='This function will expand any 10x barcode in a SampleSheet.csv to their member barcodes and print to terminal')
    parser.add_argument('-b', help='10x barcode file')
    parser.add_argument('-s', help='original SampleSheet.csv')
    args = parser.parse_args()
    return(args)


def main():
    '''
    1. in ta_barcode_dic, key is
    2. add actual seq to lib_ID_0..
    '''
    args = argsHandler()
    barcode_dic = genTAbarcodeDic(args.b)
    sample_sheet = args.s

    with open(sample_sheet) as f:
        lines = f.readlines()
        for l in lines:
            ks = [k for k in barcode_dic.keys() if k in l.split(",")]
            if (len(ks) > 0):
                ll = l.split(',')
                ll[5] = barcode_dic[ks[0]][0]
                ll[6] = ll[4]
                ll[7] = barcode_dic[ks[0]][2]
                print(','.join(ll).rstrip())
            else:
                print(l.rstrip())
    return


if __name__ == '__main__':
    main()

#!/usr/bin/env python
import argparse
import os


def genTAbarcodeDic(ta_barcode_file):
    ta_barcode_dic = {}
    # ta_barcode_file = os.path.join(
    #    'data', 'nextseq_app', 'barcodes', "chromium-shared-sample-indexes-plate.csv")
    with open(ta_barcode_file) as f:
        for line in f:
            tmpstr = line.rstrip().split(',')
            ta_barcode_dic[tmpstr[0]] = tmpstr[1:]
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
    1. add _0,_1,.. to lib_ID and barcode_name
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
                i = 1
                for b in barcode_dic[ks[0]]:
                    ll = l.split(',')
                    ll[0] += '_'+str(i)
                    ll[4] += '_'+str(i)
                    ll[5] = b
                    print(','.join(ll).rstrip())
                    i += 1
            else:
                print(l.rstrip())
    return


if __name__ == '__main__':
    main()

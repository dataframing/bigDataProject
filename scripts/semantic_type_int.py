'''
semantic_type_int.py

Check semantic type of ints
'''
import pandas as pd

def _check_zip_validity(value,nys_zips):
    '''
    validate zip codes, making sure they are within New York State
    '''
    value = int(value)
    if value in nys_zips:
        validity='valid'
    else:
        validity='invalid'
    return ('zip',validity)

zipDF = pd.read_csv('data/nys_zips_clean.tsv',sep='\t')
nys_zips = list(zipDF['ZIP Code'])

check_zip_validity = partial(_check_zip_validity,\
    nys_zips=nys_zips)


int_checks = [check_zip_validity]
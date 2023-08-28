#!/usr/bin/env python3

import os
import io
import datetime as dt
import argparse
import zipfile as zf
from shapely.geometry import shape
import json
import csv

import pandas as pd
import geopandas as gp

pd.set_option('display.max_columns', None)

# EPSG:4326 WG 84
# EPSG:32630
# EPSG:27700 OS GB36

CRS = 'EPSG:4326'
START = dt.datetime.now()

def get_opts():
    parser = argparse.ArgumentParser(description='Fix issues with the USA.zip repository')
    return()

BUFFERSIZE = 256*1024*1024

def fix_geometry(g):
    if len(c := g['geometry']['coordinates']) == 1:
        g['geometry']['type'] = 'Point'
        g['geometry']['coordinates'] = c[0]
    return shape(g['geometry'])

def get_features(gf):
    return gf['geometry'].__geo_interface__['features']

def clean_geometry(g):
    g.pop('bbox', None)
    g.pop('id', None)
    return g

def main(filestub, key):
    print(f'Load {key} data')
    infile = f'_{key}.tsv'
    try:
        os.mkdir('output')
    except FileExistsError:
        pass

    tfile = f'data/{filestub}.tsv'
    try:
        os.unlink(tfile)
    except FileNotFoundError:
        pass

    with zf.ZipFile(f'data/{key}.zip') as zfin:
        ifile = f'_{key}.tsv'
        ofile = f'output/{key}.csv'
        with zfin.open(ifile) as fin, open(ofile, 'w') as fout, open(tfile, 'w') as zout:
            ebuffer = ''
            m = 0
            while n := fin.read(BUFFERSIZE):
                now = dt.datetime.now() - START
                m += 1
                print(f'{now}\tread\toutput: {str(m).zfill(3)}')
                bbuffer = io.BytesIO(n)
                tbuffer = io.TextIOWrapper(bbuffer, encoding='utf-8').read()
                tbuffer = ebuffer + tbuffer
                lines = tbuffer.split('\n')
                ebuffer = lines.pop(-1)
                ds = pd.Series([json.loads(i) for i in lines]).apply(fix_geometry)
                gf = gp.GeoDataFrame(key, index=ds.index, geometry=ds, columns=['key'])

                now = dt.datetime.now() - START
                print(f'{now}\twrite\toutput: {str(m).zfill(3)}')
                gf.to_wkt().to_csv(fout, header=False, index=False)
                df = pd.DataFrame(key, index=gf.index, columns=['key'])
                df['geometry'] = [clean_geometry(i) for i in get_features(gf)]
                df['geometry'] = df['geometry'].apply(json.dumps)
                df.to_csv(zout, sep='\t', header=False, mode='a', index=False,
                          quoting=csv.QUOTE_NONE)

    zfile = f'data/{filestub}.zip'
    with open(tfile, 'rb') as fin, zf.ZipFile(zfile, 'w', compresslevel=9) as zout:
        m = 0
        with zout.open(f'{filestub}.tsv', 'w', force_zip64=True) as fout:
            while n:=fin.read(BUFFERSIZE):
                now = dt.datetime.now() - START
                m += 1
                print(f'{now}\twrite\tzip file: {str(m).zfill(3)}')
                fout.write(n)
    now = dt.datetime.now() - START
    print(f'{now}\tfinish\t{filestub}')

if __name__ == '__main__':
    get_opts()
    main('USA-Full', 'USA')

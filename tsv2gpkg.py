#!/usr/bin/env python3

import os
import io
import datetime as dt
import argparse
import zipfile

import pandas as pd
import geopandas as gp

pd.set_option('display.max_columns', None)

# EPSG:4326 WG 84
# EPSG:32630
# EPSG:27700 OS GB36

CRS = 'EPSG:4326'
START = dt.datetime.now()

def get_opts():
    parser = argparse.ArgumentParser(description='Convert TSV GeoJSON file to GeoPKG')

    parser.add_argument('filestub', type=str, nargs='?', help='file stub to process', default='CaribbeanIslands-Full')
    parser.add_argument('--clear-output', help='delete output files', action='store_true')
    parser.add_argument('--engine', choices=['fiona', 'pyogrio'], default='pyogrio')
    args = parser.parse_args()
    return(args.filestub, args.clear_output, args.engine)

def read_file(filepath, crs=CRS):
    data = pd.read_csv(f'{filepath}.csv', header=None, names=['key', 'geometry'])
    geometry = gp.GeoSeries.from_wkt(data['geometry'])
    return gp.GeoDataFrame(data=data, geometry=geometry).set_crs(crs)

def to_file(gf, filepath):
    df = gf.drop(columns=['geometry'])
    df['geometry'] = gf['geometry'].to_wkt()
    df.to_csv(f'{filepath}.csv', mode='ab', header=False, index=False)

def get_keys(filestub):
    keys = set()
    with zipfile.ZipFile(f'data/{filestub}.zip') as zf:
        filename = f'{filestub}.tsv'
        zf.getinfo(filename)
        with zf.open(filename) as fin:
            while n := fin.readline():
                bbuffer = io.BytesIO(n)
                line = io.TextIOWrapper(bbuffer, encoding='utf-8').read()
                k = line.split('\t').pop(0)
                if '"Feature":' in k:
                    raise(KeyError)
                keys.add(k)
    return keys

BUFFERSIZE = 512*1024*1024

def output_csv(fin, engine):
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
        df = pd.read_csv(io.StringIO('\n'.join(lines)), sep='\t', header=None)
        gf = gp.read_file(io.StringIO('\n'.join(df[1].values)), engine=engine)
        gf['key'] = df[0]
        gf = gf.set_crs(CRS)
        now = dt.datetime.now() - START
        print(f'{now}\twrite\toutput: {str(m).zfill(3)}')
        for k in gf['key'].drop_duplicates():
            now = dt.datetime.now() - START
            print(f'{now}\twrite\t{str(m).zfill(3)}:\t{k}')
            path = f'output/{k}'
            idx = gf['key'] == k
            to_file(gf[idx], path)

def to_csv(filestub, engine):
    with zipfile.ZipFile(f'data/{filestub}.zip') as zf:
        filename = f'{filestub}.tsv'
        zf.getinfo(filename)
        with zf.open(filename) as fin:
            output_csv(fin, engine)

def main(filestub, clear_output, engine='fiona'):
    infile = f'{filestub}.tsv'
    print(f'Load {filestub} data')
    keys = get_keys(filestub)
    try:
        os.mkdir('output')
    except FileExistsError:
        if clear_output:
            for root, dirs, files in os.walk('output', topdown=False):
                for name in files:
                    k = name.split('.').pop(0)
                    if k in keys:
                        os.remove(os.path.join(root, name))

    try:
        os.mkdir(filestub)
    except FileExistsError:
        pass

    create_csv = False
    for k in keys:
        path = f'output/{k}.csv'
        if not os.path.isfile(path):
            create_csv = True
            break

    if create_csv:
        print(f'File input using {engine} engine')
        to_csv(filestub, engine)

    print(f'GPKG output using {engine} engine')
    for k in keys:
        path = f'output/{k}'
        gf = read_file(path)
        now = dt.datetime.now() - START
        print(f'{now}\twrite\tgpkg:\t{k}')
        outpath = f'{filestub}/{k}.gpkg'
        gf.to_file(outpath, driver='GPKG', mode='w', layer=k, index=False, engine=engine)

    now = dt.datetime.now() - START
    print(f'{now}\tfinish\t{filestub}')


if __name__ == '__main__':
    filestub, clear_output, engine = get_opts()
    main(filestub, clear_output, engine)

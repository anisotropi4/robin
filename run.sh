#!/usr/bin/env bash

if [ ! -d venv ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install --upgrade wheel
    if [ -s requirements.txt ]; then
        pip install --upgrade -r requirements.txt | tee setup.txt
    fi
fi

source venv/bin/activate

for i in data output
do
    if [ ! -d ${i} ]; then
        mkdir ${i}
    fi
done

for URI in $(./list-files.py | sort)
do
    FILENAME=$(echo ${URI} | sed 's/^.*\///')
    FILESTUB=$(echo ${FILENAME} | sed 's/.zip//')

    echo ${FILESTUB}

    if [ ! -d ${FILESTUB} ]; then
        mkdir ${FILESTUB}
    fi

    if [ ! -s data/${FILENAME} ]; then
        curl -L -o data/${FILENAME} ${URI}
    fi

    if [ ${FILESTUB} = 'USA' ]; then
        ./fixUSA.py
        FILESTUB='USA-Full'
        mkdir ${FILESTUB}
    fi

    if [ $(ls ${FILESTUB}/*.gpkg 2> /dev/null | wc -l) -eq 0 ]; then
        echo process ${FILESTUB}
        ./tsv2gpkg.py ${FILESTUB}
    fi
done

## Note: if the USA.gpkg create fails due to insufficient memory and
## ogr2ogr will create the GPKG file from the WKT format as below

if [ ! -s USA-Full/USA.gpkg ]; then
    (echo key,WKT; cat output/USA.csv) | ogr2ogr -f GPKG USA-Full/USA-Full.gpkg CSV:/vsistdin/ -oo KEEP_GEOM_COLUMNS=NO -nln GBR -s_srs EPSG:4326 -t_srs EPSG:4326

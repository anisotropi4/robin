#!/usr/bin/env python

import os.path
from urllib.parse import urlparse, urlunparse
import requests
from bs4 import BeautifulSoup

def get_URIs(URL):
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html.parser')
    paths = []
    hit = soup.find('table')
    for a in hit.findAll('a'):
        href = a.get('href')
        if 'zip' in href:
            paths.append(href)
    return paths

def download_file(url):
    filename = url.split('/')[-1]
    filepath = f'data/{filename}'
    if os.path.isfile(filepath):
        return False
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filepath, 'wb') as fout:
            for n, chunk in enumerate(r.iter_content(chunk_size=16777216)):
                print(str(n+1).zfill(4))
                fout.write(chunk)
    return filename

def main():
    URL = 'https://github.com/microsoft/RoadDetections'

    URIs = get_URIs(URL)

    for uri in URIs:
        if 'PreMerge' in uri:
            continue
        print(uri)
    return 0

    #Use curl -L -o rather than request
    for uri in URIs:
        if 'PreMerge' in uri:
            continue
        download_file(uri)
    
if __name__ == '__main__':
    main()

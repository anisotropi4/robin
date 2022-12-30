# robin
Scripts to help make road data extracted from Microsoft Bing Maps imagery more amenable 

## Microsoft Road Detection

Microsoft Bing Maps imagery has been used to identify and extract road data [here](https://github.com/microsoft/RoadDetections). As the associated files are released under the Open Data Commons [licence](https://opendatacommons.org/licenses/odbl/) and quite big and sit in a TSV GeoJSON format repository holds this road data into individual files split by country

The GeoGPKG files are under [here](https://github.com/anisotropi4/shambles/tree/main/transport-network)

### Development

The project is developed in `python3` and `bash` shell script on Linux Mint, and will attempt to download, process and create `GeoPackage`. However this can take quite a long time as the data is quite big

### Execution

This assumes that you have a working `bash` and base `python3` environment and the `curl` command line tool for getting data from a URL. To run the project type

   $ ./run.sh

This will create a `python` `virtual environment`, install package dependencies and then attempt to down and processes all of the files on the Microsoft repository

## Licenses

My thanks to Microsoft for publishing this data set and making it freely available for download and use under the [Open Data Commons Open Database License (ODbL)](https://opendatacommons.org/licenses/odbl).

The code is released under the [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0.html) and the derived data is published in a separate repository [here](https://github.com/anisotropi4/shambles/tree/main/transport-network) under the [Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/)

## Thanks 

Thanks to [Alistair Rae](https://twitter.com/undertheraedar) for letting me know about this

Will

[@WillDeakin1](https://twitter.com/WillDeakin1)
[@wnd](https://fosstodon.org/@wnd)




 


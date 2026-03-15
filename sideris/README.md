# Sideris Ephemerides API Service

This readme explains how to use *Sideris* to calculate and serve ephemerides for star/DSO and Solar System objects.

This folder contains two utilities with different functionality for `Sideris`.

## **Catalog fetching** (`catalog_fetch.py`)

This is a CLI containing the logic to fetch and create the sidereal catalog and the constellation data used by *Sideris*. 

It fetches data from `Simbad` and `VizieR` to look up star and DSO data and merge it in a single, sidereal catalog generated in both JSON and pickle (`.pkl`) formats. 

For the constellations, it uses the constellation data `constellationship.fab` from Stellarium source code to generate a friendlier JSON catalog with a better formatting for *Sideris*

By default, fetches *HIP* catalog for stars and *Messier*, *NGC* and *IC* catalogs for DSO, along with some manual added objects not found on those catalogs that can be configured through `config.py`.

I've defined a BaseProvider to allow new catalog fetching, although you may want to later merge the results with the other catalogs (inside `catalog_fetch.py`)

## **Sideris API** (`sideris.py`)

This is the main ephemerides service that takes as inputs the sidereal catalog data (`sidereal_catalog.pkl`) and the constellation catalog data (`constellationship.json`) and serves the metadata and the ephemerides calculations using `Astropy`, `Astroplan` and `SkyField`.


## Usage

### Preinstallation

First it's necessary to install the appropriate python packages. You can use the `requirements.txt` file for that:

```bash
pip install -r requirements.txt
```

### Catalog Generation

*Sideris* requires to have the two catalog files containing the sidereal data and the constellation data (`data/sidereal_catalog.pkl` and `data/constellationship.json`).

By default, they're included in this repo inside `data`, but if you want to update or generate new catalogs you can run `catalog_fetch.py`. 

To do so, you can use the default configuration or use your own:

```bash
python catalog_fetch.py
```

For example, if you want a lighter catalog with only visible stars (magnitude < 4.0) you can use:

```bash
python catalog_fetch.py -m 4.0 -o data/light_catalog
```

Some of the available options include:

- *-ci*, *--const-input*: Path to the .fab file containing the constellation data (`data/constellationship.fab` by default)
- *-co*, *--const-output*: Path to save the constellation data (`data/constellationship.json` by default)
- *-o*, *--output*: Path to save the sidereal catalog data in json and pkl *without file extension* (`data/sidereal_catalog` by default)
- *-m*, *--mag-limit*: Maximum star magnitude (6.0 by default)
- *-d*, *--dist-threshold*: Distance threshold for near object merging (2.5 arcmin by default)
- *-ns*, *--no-stats*: Hide the last stats summary

After execution, your `data/` folder will look like this:

```
data/
 ├── constellationship.fab    # Original input
 ├── constellationship.json   # Generated (IAU IDs mapping)
 ├── sidereal_catalog.json    # Generated (Human-readable catalog)
 └── sidereal_catalog.pkl     # Generated (Fast-loading binary for the API)
```

Note that it will download all stars needed for all constellations, no matter their magnitude.

### Running the API

Once generated, you can run the API using:

```bash
uvicorn sideris:app --host <your host> --port <your port>
```
or use it with default arguments (127.0.0.1:8624)
```bash
python sideris.py
```

[![Build Status](https://travis-ci.org/materialscloud-org/structure-property-visualizer.svg?branch=master)](https://travis-ci.org/materialscloud-org/structure-property-visualizer)

# Structure-Property-Visualizer

Use this app to generate interactive visualizations like [these](https://www.materialscloud.org/discover/cofs#mcloudHeader)
for atomic structures and their properties.

### UPDATE (September 2020)
Now this package contains the `results` and `details` pages copied from `nanoporous_screening` to display different 
applications for COFs. This will be used to produce a permanent reference for the ACS Central Science's Outlook. 

Not to have a dependency to the `nanoporous_screening/pipeline` package, the needed functions are copied in the 
`pipeline_emul.py` files in the `results` and `details` directories (two identical files).

## Inner working

For each COF we create a group, e.g., `discover_curated_cofs/05001N2` that contains all the nodes that are relevant for that structure.
These nodes have the extra `TAG_KEY`, which indicates the content of that node: e.g., `orig_cif`, `opt_cif_ddec`, `isot_n2`, ...
Currently `GROUP_DIR = "discover_curated_cofs/"` and `TAG_KEY = "tag4"`, but they may vary in the future.

## Re-implementation based on Panel

Use as jupyter notebook:
```
jupyter notebook
# open figure/main.ipynb
```

Use with panel:
```
panel serve detail/ figure/
```

## Features

 * interactive scatter plots via [bokeh server](https://bokeh.pydata.org/en/1.0.4/)
 * interactive structure visualization via [jsmol](https://chemapps.stolaf.edu/jmol/docs/)
 * simple input: provide CIF/XYZ files with structures and CSV file with their properties
 * simple deployment on [materialscloud.org](https://www.materialscloud.org/discover/menu) through [Docker containers](http://docker.com)
 * driven by database backend:
   1. [sqlite](https://www.sqlite.org/index.html) database (default)
   1. [AiiDA](http://www.aiida.net/) database backend (less tested)

## Getting started

### Prerequisites

 * [git](https://git-scm.com/)
 * [python](https://www.python.org/) >= 2.7
 * [nodejs](https://nodejs.org/en/) >= 6.10

### Installation

```
git clone https://github.com/materialscloud-org/structure-property-visualizer.git
cd structure-property-visualizer
pip install -e .     # install python dependencies
./prepare.sh         # download test data (run only once)
```

### Running the app

```
bokeh serve --show figure detail select-figure   # run app
```

## Customizing the app

### Input data
 * a set of structures in `data/structures`
   * Allowed file extensions: `cif`, `xyz`
 * a CSV file `data/properties.csv` with their properties
   * has a column `name` whose value `<name>` links each row to a file in `structures/<name>.<extension>`.
 * adapt `import_db.py` accordingly and run it to create the database

### Plots

The plots can be configured using a few YAML files in `figure/static`:
 * `columns.yml`: defines metadata for columns of CSV file
 * `filters.yml`: defines filters available in plot
 * `presets.yml`: defines presets for axis + filter settings

## Docker deployment

```
pip install -e .
./prepare.sh
docker-compose build
docker-compose up
# open http://localhost:3245/cofs/select-figure
```

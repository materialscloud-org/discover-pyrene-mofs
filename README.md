# Discover Pyrene-MOFs

Interactive resources associated with the review paper on MOFs with pyrene ligands.

## Getting started

### Prerequisites

 * [git](https://git-scm.com/)
 * [python](https://www.python.org/) >= 2.7
 * [nodejs](https://nodejs.org/en/) >= 6.10

### Installation

```
git clone https://github.com/{thispackage}
cd {thispackage}
pip install -e .     # install python dependencies
./prepare.sh         # download test data (run only once)
```

### Running the app

```
bokeh serve --show figure select_pyrenemofs
```

## Docker deployment

 * Adapt variables in `docker-compose.yml` to fit the connection details of your AiiDA database
 * For MacOS, use `AIIDADB_HOST: docker.host.internal` and comment out `network_mode`
 * For Linux, use `AIIDADB_HOST: 127.0.0.1` and use `network_mode: host`

```
docker-compose build
docker-compose up
# open http://localhost:5006/pyrene-mofs/select_pyrenemofs
```

# Discover Pyrene-MOFs

Interactive resources associated with the review paper on MOFs with pyrene ligands.

## Getting started

### Prerequisites

- [git](https://git-scm.com/)
- [python](https://www.python.org/) >= 2.7
- [nodejs](https://nodejs.org/en/) >= 6.10

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

This has been built as a docker image and is deployed on MaterialsCloud. This docker image is availible on the private MaterialsCloud harbor registry.
If you would like to rebuild this container. You will need the [pyrene_mofs.aiida](https://archive.materialscloud.org/record/2020.156) aiida database file at the same level as the Dockerfile.

Rebuilding is then simple.

```
docker compose build
docker compose up
# open http://localhost:5006/select_pyrenemofs
```

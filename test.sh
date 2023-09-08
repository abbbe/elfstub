#!/bin/sh -xe

# build the dummy program used for tests
apk add gcc
gcc -g src/dummy.c -o tests/dummy

source venv/bin/activate

## python -m pytest tests/*.py -v

# binary patching works
python -m pytest -v tests/bin_*.py

# fails on alpine but works on ubuntu22
python -m pytest -v tests/lib_*.py || true

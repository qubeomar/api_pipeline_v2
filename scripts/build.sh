#!/bin/bash
pip install tox wheel
pip list
tox --recreate -e py3 -e lint
scripts/version_gen.sh
python setup.py bdist_wheel

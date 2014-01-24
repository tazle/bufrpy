#! /bin/sh
virtualenv py
py/bin/pip install bitstring sphinx
virtualenv -p python3 py3
py3/bin/pip install bitstring

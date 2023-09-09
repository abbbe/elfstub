#!/bin/sh -xe

apk add python3 py3-pip py3-virtualenv

python3 -m venv venv
source venv/bin/activate
python3 -m pip install -U pip

pip install -r requirements.txt

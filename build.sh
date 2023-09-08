#!/bin/sh -xe

apk add python3 py3-pip gcc python3-dev musl-dev linux-headers tmux npm bash

python3 -m pip install -U pip
python3 -m pip install -U virtualenv

python3 -m virtualenv venv
source venv/bin/activate

pip install -r requirements.txt

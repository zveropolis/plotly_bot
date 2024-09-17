#!/usr/bin/bash

pid=$(ps aux | grep venv | grep -v grep | grep _main | tr -s [:blank:] | tr [:blank:] \\n | sed '2!d')

if [[ -z $pid ]]
then
    cd ~/code/vpn_dan_bot
    git pull
    poetry install --without dev
    ./_main.py --nolog console
fi
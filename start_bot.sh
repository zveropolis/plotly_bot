#!/usr/bin/bash

pid=$(ps aux | grep venv | grep -v grep | grep _main | tr -s [:blank:] | tr [:blank:] \\n | sed '2!d')

if [[ -z $pid ]]
then
    cd ~/code/plotly_bot
    ./_main.py -m cycle --nolog console
fi
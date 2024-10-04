#!/bin/bash

source ../venv/bin/activate

while /bin/true;
do

PYTHON_SEARCH_PATH=../ python _journal_monitor.py
sleep 120

done

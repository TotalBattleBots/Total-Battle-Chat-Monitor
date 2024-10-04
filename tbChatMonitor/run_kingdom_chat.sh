#!/bin/bash

source ../venv/bin/activate

while /bin/true;
do
PYTHON_SEARCH_PATH=../ python _kingdom_chat.py
sleep 120

done

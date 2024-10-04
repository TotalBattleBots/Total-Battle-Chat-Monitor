#!/bin/bash

source ../venv/bin/activate

while /bin/true;
do

PYTHON_SEARCH_PATH=../ python _group_chats.py
sleep 120

done

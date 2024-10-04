#!/bin/bash

start=0x0000
end=0x1FFFFF

for (( code=$start; code<=$end; code++ ))
do
	emoji=$(printf "\U$(printf '%x' $code)")
	python3 list_chats.py "$emoji"
done



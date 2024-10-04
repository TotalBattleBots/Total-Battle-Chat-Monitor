#!/bin/bash

start=0x0000
end=0x00FF

for (( code=$start; code<=$end; code++ ))
do
	emoji=$(printf "\U$(printf '%x' $code)")
	python3 list_chats.py "$emoji"
done



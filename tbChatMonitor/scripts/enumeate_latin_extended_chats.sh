#!/bin/bash

# Russian
start=0x0100
end=0x017F

for (( code=$start; code<=$end; code++ ))
do
	emoji=$(printf "\U$(printf '%x' $code)")
	python3 list_chats.py "$emoji"
done


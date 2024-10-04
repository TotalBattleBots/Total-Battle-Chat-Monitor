#!/bin/bash

start=0x1F300
end=0x1F6FF

for (( code=$start; code<=$end; code++ ))
do
	emoji=$(printf "\U$(printf '%x' $code)")
	echo "$code - $emoji"
	python3 list_chats.py "$emoji"
done


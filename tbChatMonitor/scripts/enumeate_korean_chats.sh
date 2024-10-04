#!/bin/bash

# Korean


start=0xAC00
end=0xD7AF

for (( code=$start; code<=$end; code++ ))
do
	emoji=$(printf "\U$(printf '%x' $code)")
	python3 list_chats.py "$emoji"
done

start=0x1100
end=0x11FF

for (( code=$start; code<=$end; code++ ))
do
	emoji=$(printf "\U$(printf '%x' $code)")
	python3 list_chats.py "$emoji"
done

start=0x3130
end=0x318F

for (( code=$start; code<=$end; code++ ))
do
	emoji=$(printf "\U$(printf '%x' $code)")
	python3 list_chats.py "$emoji"
done




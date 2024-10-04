#!/bin/bash

# Russian
start=0x0400
end=0x052F

for (( code=$start; code<=$end; code++ ))
do
	emoji=$(printf "\U$(printf '%x' $code)")
	python3 list_chats.py "$emoji"
done

start=0x2DE0
end=0x2DFF

for (( code=$start; code<=$end; code++ ))
do
	emoji=$(printf "\U$(printf '%x' $code)")
	python3 list_chats.py "$emoji"
done

start=0xA640
end=0xA69F

for (( code=$start; code<=$end; code++ ))
do
	emoji=$(printf "\U$(printf '%x' $code)")
	python3 list_chats.py "$emoji"
done


start=0x1C80
end=0x1C8F

for (( code=$start; code<=$end; code++ ))
do
	emoji=$(printf "\U$(printf '%x' $code)")
	python3 list_chats.py "$emoji"
done


# Korean



#!/bin/bash
shopt -s expand_aliases
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

source $SCRIPT_DIR/../venv/bin/activate

kingdoms="37 51 56 64 70 82 83 84 85 86 87 88 89 90 91 92 93 94 95 96 97 98 99 100 101 102 103 104 105 106 107 108 109 110 111 112 116"

clans="146028888242 356482285618 317827583044 2147483648069 373662155436"
pushd $SCRIPT_DIR
for i in $kingdoms; do
    python ./player_database.py -k $i
done

for in in $clans; do
  python ./player_database.py -c $i
done
printf "Hello, world!\n"

popd


#!/bin/bash
set -e
# apts
# $sudo apt install python3-pip
# 
# python
# pip3 install redis

rm -f tmp_file
while :
do
  python3 calc_ranking.py ./calc_score ./maps
done

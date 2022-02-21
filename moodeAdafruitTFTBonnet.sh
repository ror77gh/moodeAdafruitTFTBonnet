#!/bin/bash
 
while getopts ":sq" opt; do
  case ${opt} in
    s ) sudo pkill -f moodeAdafruitTFTBonnet.py; sudo /usr/bin/python3 /home/pi/moodeAdafruitTFTBonnet/clear_display.py; sudo /usr/bin/python3 /home/pi/moodeAdafruitTFTBonnet/moodeAdafruitTFTBonnet.py &
      ;;
    q ) sudo pkill -f moodeAdafruitTFTBonnet.py; sudo python3 /home/pi/moodeAdafruitTFTBonnet/clear_display.py
      ;;
    \? ) echo "Usage: cmd [-s] [-q]"
      ;;
  esac
done
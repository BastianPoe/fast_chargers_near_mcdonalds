#!/bin/bash

echo Downloading all Chargers
python3 all_chargers.py
echo

echo Downloading all McDonalds
python3 mcdonalds.py
echo

echo Matching McDonalds and Chargers + quering Google Maps
python3 combine.py
echo

echo Generating kml
python3 generate_map.py
echo Generated chargers.kml
echo

echo done

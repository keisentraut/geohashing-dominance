#!/usr/bin/bash


# download fippes data
curl https://fippe.de/alldata.js |
  sed 's/var expeditions = //' |
  head -c -5 > alldata.js
echo "]" >> alldata.js

# colors
python colors.py

# create directories
for zoom in $(seq 0 9); do
	for x in $(seq 0 $((2**zoom-1)) ); do
		mkdir -p output/$zoom/$x/
		mkdir -p cache/$zoom/$x/
		for y in $(seq 0 $((2**zoom-1)) ); do
    			echo python ./tile.py $zoom $x $y
		done
	done
done | parallel -j 8 # 8 CPU cores

# larger than zoom level 8 is too big for my RAM - final image is too large
for zoom in $(seq 0 8); do
	python ./combine.py $zoom	
done

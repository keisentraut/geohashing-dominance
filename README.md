# What is this?

[Geohashing](https://geohashing.site/geohashing/) is a game based on [XKCD comic #426](https://xkcd.com/426/).
It generates a daily, random location close to you and the challenge is to visit that location on the same day.
There are a few active users and I had the idea to create a world map which shows which user is most active in a given area. 
This repository contains the Python scripts to create such a visualization similiar to OSM tiles.

# Usage

Start with ```calc_all.sh```. The most interesting file is probably ```tile.py```.

# FAQ

## Which color is which user?

Look at ```colors.py```. The script uses a pseudo-random deterministic functoin which assigns a random RGB color to each username.

## How can I view it?

One of Germany's most active geohashers created an [interactive map](https://fippe.de/dominance).

# !/usr/bin/python

import json
from math import radians, cos, sin, asin, sqrt, exp, atan, sinh, degrees, asinh, pi, tan
from copy import deepcopy
import os.path
import requests
from PIL import Image
import random
import sys
import time
import hashlib

# usage: ./tile.py zoom x y 
zoom,x,y = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
n = 1<<zoom

# https://fippe.de/alldata.js, but preprocessed to be valid JSON
with open("alldata.js","r") as f:
    data = json.load(f)
    # filter only reached hashes, convert to radians, throw away unnecessary stuff like achievements
    data = [[i[0],i[1]/180*pi,i[2]/180*pi,i[3]] for i in data if i[4] == True]

def num2rad(xtile, ytile):
    lat_rad = atan(sinh(pi * (1 - 2 * ytile / n)))
    lon_rad = (xtile / n * 2 - 1)*pi 
    return lat_rad, lon_rad

maxlat, minlon = num2rad(x,y) 
minlat, maxlon = num2rad(x+1,y+1)
print(f"tile {x}x{y} at zoom {zoom} is from N{maxlat/pi*180} E{minlon/pi*180} to N{minlat/pi*180} E{maxlon/pi*180}")
# now download tiles if necessary
fname = f"osmcache/{zoom}/{x}/{y}.png"
url = f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
if not os.path.isfile(fname):
    print(f"downloading {fname} from {url}")
    headers={'user-agent': 'klaus-openstreetmap@hohenpoelz.de'}
    # WARNING: This probably violates OSM policy and I don't really need it - so I commented it out.
    #r=requests.get(url, headers=headers)
    #with open(fname, 'wb') as f:
    #    f.write(r.content)

# we prefilter all geohashes not relevant
BORDER = 0.04 # 0.018 radians is 1.031 degree
data = [i for i in data if minlat-BORDER < i[1] < maxlat+BORDER]
data = [i for i in data if minlon-BORDER < i[2] < maxlon+BORDER]
users = set()
for i in data:
    users |= set(i[3])
print(f"after prefiltering there are {len(data)} hashes and {len(users)} users left")

# deterministic color selection
def getcolor(username):
    HARD_COLORS= {"Klaus":(255,0,0), "Fippe":(0,255,0), "GeorgDerReisende":(0,0,255)}
    if username in HARD_COLORS:
        return HARD_COLORS[username]
    r,g,b = 0,0,0
    username=username.encode('utf8')
    while not r+g+b > 256 and r+g+b<256*3-256: # not too dark and not too light
        username = hashlib.md5(username).digest() 
        r,g,b = username[0], username[1], username[2]
    return (r,g,b)
colors = {u:getcolor(u) for u in users}

dominators = Image.new('RGB', (256,256), (0,0,0))
tmp = dict.fromkeys(users,0.)

x_width_per_pixel = (maxlon-minlon)/256
y_width_per_pixel = (maxlat-minlat)/256

lon,lat = minlon, maxlat
lon = minlon + (x_width_per_pixel*0.5) # use center of pixel
for i in range(256):
    lat = maxlat - (y_width_per_pixel*0.5) # use center of pixel
    for j in range(256):
        # reset weights
        for index in tmp: 
            tmp[index] = 0. 
        for geohash in data:
            geolat, geolon = geohash[1], geohash[2]
            dlon = geolon - lon
            dlat = geolat - lat
            if -BORDER <= dlon <= BORDER:
                if -BORDER <= dlat <= BORDER:
                    # https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points/4913653#4913653
                    a = sin(dlat/2)**2 + cos(lat) * cos(geolat) * sin(dlon/2)**2
                    # This would be correct: d = 12742 * asin(sqrt(a)) 
                    # but we want 1/(d*d+1) == 0.5 if the distance is 10km, so we divide by 10
                    d = 1274.2 * asin(sqrt(a)) 
                    if d < 10: # less than 100km
                        w = 1/(d*d + 1)
                        for geouser in geohash[3]:
                            tmp[geouser] += w
        if tmp:
            max_user = max(tmp, key=tmp.get)
            if tmp[max_user] > 0:
                kings.putpixel([i,j], colors[max_user])
                #print(f"winner at N{lat/pi*180} E{lon/pi*180} is {max_user} {colors[max_user]}")
        lat -= y_width_per_pixel
    lon += x_width_per_pixel
dominators.save(f"output/{zoom}/{x}/{y}.png")


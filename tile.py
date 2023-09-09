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
import colorsys

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
BORDER = 0.03 # 0.03 radians is 1.71 degree which is most often more than 100km except in some very north locations
data = [i for i in data if minlat-BORDER < i[1] < maxlat+BORDER]
data = [i for i in data if minlon-BORDER < i[2] < maxlon+BORDER]
users = set()
for i in data:
    users |= set(i[3])
print(f"after prefiltering there are {len(data)} hashes and {len(users)} users left")

# deterministic color selection based on username
with open("colors.json", "r") as f:
    colors = json.loads(f.read()) 
colors = {i:(j[0],j[1],j[2]) for i,j in colors.items()}

# checkerboard function recommended in discord by Stevage
def getmaxuser(tmp, i,j):
    max_count = max(tmp.values())
    max_users = {user: count for user, count in tmp.items() if count == max_count}
    sorted_users = sorted(max_users.items(), key=lambda x: x[0])
    v = (i//10+j//10)
    return sorted_users[v % len(sorted_users)][0]

# weight function, input is in multiples of 10km
def getweight(d):
    if d>1: return 0 # cutoff at 100km
    # weights in 0, 10, 20, .., 100km are [1.0, 0.81, 0.64, 0.49, 0.36, 0.25, 0.16, 0.09, 0.04, 0.01, 0.0]
    # calculated by [round((1-d/100)*(1-d/100),4) for d in range(0,101,10)]
    return (1-d)*(1-d)

dominators = Image.new('RGB', (256,256), (0,0,0))
tmp = dict.fromkeys(users,0.)

x_width_per_pixel = (maxlon-minlon)/256
y_width_per_pixel = (maxlat-minlat)/256

lon,lat = minlon, maxlat
lon = minlon + (x_width_per_pixel*0.5) # use center of pixel
if len(data)>0:
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
                        # but we want multiples of 100km, so divide by 100
                        d = 127.42 * asin(sqrt(a)) 
                        w = getweight(d)
                        for geouser in geohash[3]:
                            tmp[geouser] += w
            if tmp:
                max_user = getmaxuser(tmp, i, j)
                if tmp[max_user] > 0:
                    dominators.putpixel([i,j], colors[max_user])
                    #print(f"winner at N{lat/pi*180} E{lon/pi*180} is {max_user} {colors[max_user]}")
            lat -= y_width_per_pixel
        lon += x_width_per_pixel
dominators.save(f"output/{zoom}/{x}/{y}.png")


# !/usr/bin/python

import json
import hashlib
import colorsys

# https://fippe.de/alldata.js, but preprocessed to be valid JSON
with open("alldata.js","r") as f:
    data = json.load(f)

# filter only reached hashes, convert to radians, throw away unnecessary stuff like achievements
data = [[i[0],i[1],i[2],i[3]] for i in data if i[4] == True] 

users = set()
for i in data:
    users |= set(i[3])

# deterministic color selection based on username
def getcolor(username):
    # we need something deterministic but pseudo random
    # as geohashing uses MD5, let's use MD5 for pseudorandom function, too
    username=username.encode('utf8')
    username = hashlib.md5(username).digest()
    # we want colors in HSL space 
    # hue 0-360, saturation 0.5-1 and luminosity 0.25-0.75.
    h = int.from_bytes(username[0:2], "big") / (256*256) # use two bytes because we have 360 options
    s = 0.5 + username[2]/512
    l = 0.25  + username[3]/512
    # convert HSL -> RGB
    r,g,b = colorsys.hls_to_rgb(h,l,s)
    r,g,b = int(r*256), int(g*256), int(b*256)
    print(f"HSL({h}, {s}, {l}) == RGB({r}, {g}, {b})")
    return (r,g,b)
colors = {u:getcolor(u) for u in users}

# username -> list of pixels dominated
with open("colors.json", "w") as f:
    f.write(json.dumps(colors))

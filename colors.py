# !/usr/bin/python

import json
import hashlib
# https://fippe.de/alldata.js, but preprocessed to be valid JSON
with open("alldata.js","r") as f:
    data = json.load(f)

# filter only reached hashes, convert to radians, throw away unnecessary stuff like achievements
data = [[i[0],i[1],i[2],i[3]] for i in data if i[4] == True] 

users = set()
for i in data:
    users |= set(i[3])

def randomcolor(username):
    HARD_COLORS= {"Klaus":(255,0,0), "Fippe":(0,255,0), "GeorgDerReisende":(0,0,255)}
    if username in HARD_COLORS:
        return HARD_COLORS[username]
    r,g,b = 0,0,0
    username=username.encode('utf8')
    while not r+g+b > 256 and r+g+b<256*3-256: # not too dark and not too light
        username = hashlib.md5(username).digest() 
        r,g,b = username[0], username[1], username[2]
    return (r,g,b)

# username -> list of pixels dominated
colors = {u:randomcolor(u) for u in users}
with open("colors.txt", "w") as f:
    f.write(str(colors))

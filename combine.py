#!/usr/bin/python

import sys
from PIL import Image

zoom = int(sys.argv[1])
n = 2**zoom

width,height = n*256,n*256

# osm
i = Image.new('RGBA', (width,height), (255,255,255))
for x in range(n):
    for y in range(n):
        tmp=Image.open(f"cache/{zoom}_{x}_{y}.png")
        i.paste(tmp, box=(x*256, y*256))
i.save(f"combined/{zoom}_osm.png")
# kings
i = Image.new('RGBA', (width,height), (255,255,255))
for x in range(n):
    for y in range(n):
        tmp=Image.open(f"output/{zoom}_{x}_{y}.png")
        i.paste(tmp, box=(x*256, y*256))
i.save(f"combined/{zoom}_king.png")

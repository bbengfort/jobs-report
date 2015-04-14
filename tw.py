#!/usr/bin/env python

import csv
import json

data = []

print "["
with open('fixtures/unemprate.csv', 'r') as f:
    reader = csv.reader(f)

    idx = 1
    for row in reader:
        sid   = row[1]
        title = row[2]
        state = title.split(",")[0]

        if "Puerto Rico" in title:
            continue

        fips  = "US%02i" % idx

        data.append((sid, state, fips))
        print "    %s," % repr((sid, state, fips))

        idx += 1
        if idx in (3, 7, 11, 14, 43, 52):
            idx += 1
print "]"

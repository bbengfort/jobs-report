# ingest.wrangle
# Converts the ingested data into a single CSV file
#
# Author:   Benjamin Bengfort <bengfort@cs.umd.edu>
# Created:  Wed Mar 11 11:54:17 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: wrangle.py [] bengfort@cs.umd.edu $

"""
Converts the ingested data into a single CSV file.

This code should be added to the ingest methodology.
"""

##########################################################################
## Imports
##########################################################################

import os
import csv
import glob
import json

from fetch import FIXTURES
from fetch import TimeSeries
from datetime import datetime
from operator import itemgetter
from version import get_version
from collections import defaultdict

DATE_FMT = "%B %Y"
JSON_FMT = "%Y-%m-%dT%H:%M:%S.%f"

##########################################################################
## Helper Functions
##########################################################################


def extract(path):
    """
    Extracts timeseries data from a JSON file and returns a list of tuples
    in the form of (date, value). This will also return the "Series ID" for
    reference in other methods.
    """

    # important variables
    series_id = None
    series    = {}

    # extract data from JSON
    with open(path, 'r') as f:
        data = json.load(f)
        series_id = data['seriesID']
        for row in data['data']:
            date = datetime.strptime("%(periodName)s %(year)s" % row, DATE_FMT).date()
            series[date] = row['value']

    return series_id, series


def wrangle(date=None):
    """
    Takes an ingestion data and loads the data found in that directory.
    Returns the data and the data directory as found by the date.
    """

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    dir = os.path.join(FIXTURES, "ingest-%s" % date)
    if not os.path.exists(dir) or not os.path.isdir(dir):
        raise Exception("Could not find directory named '%s'" % dir)

    # Key is the date, value is a dict of series_id:value
    data = defaultdict(dict)
    for path in glob.glob(os.path.join(dir, "*.json")):
        series_id, values = extract(path)
        for date, value in values.items():
            data[date][series_id] = value

    return dir, data


def wrangle_csv(date=None, out=None):
    """
    Takes an ingest date and then wrangles the data found in that directory to
    a CSV format that can be used to import data into a database system.
    """

    dir, data = wrangle(date)

    if out is None:
        out  = os.path.join(dir, "dataset.csv")

    fields = ("YEAR", "MONTH", ) + tuple(TimeSeries.keys())
    rows   = 0
    with open(out, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for date, values in sorted(data.items(), key=itemgetter(0), reverse=True):
            values["YEAR"]  = date.year
            values["MONTH"] = date.month
            writer.writerow(values)
            rows += 1

    return out, rows


def wrangle_json(date=None, out=None, indent=None):
    """
    Takes an ingest date and then wrangles the data found in that directory to
    a JSON format specifically required by the ELMR application.
    """

    dir, data = wrangle(date)

    if out is None:
        out  = os.path.join(dir, "elmr.json")

    ## Create output dictionary
    output = {
        "title": "ELMR Ingested BLS Data",
        "version": get_version(),
        "ingested": date,
        "wrangled": datetime.now().strftime(JSON_FMT),
        "descriptions": TimeSeries,
        "data": [],
    }

    rows = 0
    for date, values in sorted(data.items(), key=itemgetter(0), reverse=True):
        values["YEAR"]  = date.year
        values["MONTH"] = date.month
        output["data"].append(values)
        rows += 1

    with open(out, 'w') as f:
        json.dump(output, f, indent=indent)

    return out, rows

if __name__ == '__main__':
    wrangle_json("2015-03-10")
    # print extract(os.path.join(FIXTURES, "ingest-2015-03-10", "LNS11000000.json"))

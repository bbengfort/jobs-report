# elmr.ingest.wrangle
# Wrangles data into the ELMR database
#
# Author:   Benjamin Bengfort <bengfort@cs.umd.edu>
# Created:  Wed Mar 11 11:54:17 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: wrangle.py [] bengfort@cs.umd.edu $

"""
Wrangles data into the ELMR database
"""

##########################################################################
## Imports
##########################################################################

import os
import glob
import json
import elmr

from datetime import datetime
from operator import itemgetter

from elmr.models import SeriesRecord, Series

##########################################################################
## Module Constants
##########################################################################

DATE_FMT = "%B %Y"
JSON_DTE = "%Y-%m-%d"
JSON_FMT = "%Y-%m-%dT%H:%M:%S.%f"

##########################################################################
## Wrangling Functions
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
            dtstr = "%(periodName)s %(year)s" % row
            date  = datetime.strptime(dtstr, DATE_FMT).date()

            series[date] = row['value']

    return series_id, series


def wrangle(path):
    """
    Takes a path to ingested data then loads the data found in that directory.
    Adds all of the data to the database returning the  number of rows found,
    and the number of unique rows added.
    """

    rows_fetched = 0
    rows_added   = 0

    for path in glob.glob(os.path.join(path, "*.json")):
        # For each JSON file in the path, extract the data
        series_id, values = extract(path)

        # Fetch the series from the database
        series = Series.query.filter_by(blsid=series_id).first()

        # Insert data into the database in order
        for date, value in sorted(values.items(), key=itemgetter(0)):
            rows_fetched += 1

            # Search for a row that contains this combination
            q = SeriesRecord.query.filter_by(
                series_id=series.id, period=date, value=value
            )

            if not elmr.db.session.query(q.exists()).scalar():
                r = SeriesRecord(
                    series_id=series.id,
                    period=date,
                    value=float(value),
                )
                elmr.db.session.add(r)

                rows_added += 1

        # Commit each series individually
        elmr.db.session.commit()

    return rows_added, rows_fetched

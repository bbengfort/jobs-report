# elmr.ingest.fetch
# Fetches the important data sets and saves them as a table by year
#
# Author:   Benjamin Bengfort <bengfort@cs.umd.edu>
# Created:  Tue Mar 10 12:06:04 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: fetch.py [] bengfort@cs.umd.edu $

"""
Fetches the important data sets and saves them as a table by year.

Basically this simple script fetches API data from the BLS website and
stores it in a fixtures directory for wrangling.

Method:

    1. Fetch data from BLS API and save to disk
    2. Wrangle data into database
    3. Clean up data fetched onto disk

The wrangle module is still there for other helper functions.
"""

##########################################################################
## Imports
##########################################################################

import os
import json
import time
import shutil
import datetime

from elmr.config import Config
from elmr.models import Series
from elmr.models import SeriesRecord
from elmr.models import IngestionRecord
from elmr.ingest.blsapi import bls_series

##########################################################################
## Module Constants
##########################################################################

STARTYEAR  = Config.STARTYEAR   # Fetch start
ENDYEAR    = Config.ENDYEAR     # Fetch end
FIXTURES   = Config.FIXTURES    # Fixtures directory


##########################################################################
## Fetch Methods
##########################################################################

def ingest_path(root):
    """
    Returns a directory to temporarily hold intermediary data files. Creates
    the directory if it does not exist to make things easier.

    Considered using a temp directory - but thought we should allow the user
    the option to keep the ingested JSON files on disk if they so desired.
    """

    dname  = "ingest-%s" % datetime.datetime.now().strftime("%Y-%m-%d")
    folder = os.path.join(root, dname)

    if not os.path.exists(folder):
        os.makedirs(folder)

    return folder


def fetch_series(sids, path, startyear=STARTYEAR, endyear=ENDYEAR):
    """
    Fetches a set of series and writes their temporary JSON files to disk at
    the path specified. This method should be used to fetch about 10 or so
    series at a time from the BLS API, and store to disk.
    """

    # Make API call for series id set
    data   = bls_series(sids, startyear=STARTYEAR, endyear=ENDYEAR)

    # Upon response, write results to disk
    for dataset in data['Results']['series']:
        fname = os.path.join(path, "%s.json" % dataset['seriesID'])
        with open(fname, 'w') as f:
            json.dump(dataset, f)


def fetch_all(startyear=STARTYEAR, endyear=ENDYEAR, fixtures=FIXTURES,
              blocksize=10, cleanup=True, ratelimit=1, callback=None):
    """
    Fetches the data for all series ids that are in the database by ingesting
    them in blocks of 10 time series at a time for the given start and end
    years. The method is implemented as follows:

        1. Determine disk directory to write to via fixtures
        2. Look up series ids from the database
        3. Fetch blocksize number of series at a time with start and end year
        4. Rate limit the fetch by the number of seconds passed
        5. Call the callback function, passing the directory of data
        6. If cleanup, delete the directory and its contents

    The callback methodology allows you to create a fetch-wrangle chain.

    This method returns the duration and the number of timeseries fetched,
    as well as any results from the callback.
    """

    start = time.time()
    store = ingest_path(fixtures)
    count = Series.query.count()
    pages = count / blocksize

    for pagenum in xrange(1, pages + 2):
        page = Series.query.paginate(pagenum, blocksize, False)
        sids = [s.blsid for s in page.items]

        fetch_series(sids, store, startyear, endyear)
        time.sleep(ratelimit)

    cbres = None
    if callback is not None and callable(callback):
        cbres = callback(store)

    if cleanup:
        shutil.rmtree(store)

    delta = time.time() - start
    return delta, count, cbres

##########################################################################
## Main Method
##########################################################################

if __name__ == '__main__':
    fetch_all()

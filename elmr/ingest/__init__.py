# elmr.ingest
# Data ingestion from the BLS API
#
# Author:   Benjamin Bengfort <bengfort@cs.umd.edu>
# Created:  Mon Mar 09 16:01:32 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: __init__.py [] bengfort@cs.umd.edu $

"""
Data ingestion from the BLS API
"""

##########################################################################
## Imports
##########################################################################

import elmr

from elmr.config import Config
from datetime import date, datetime
from elmr.models import IngestionRecord
from elmr.ingest import fetch, wrangle


def ingest(**kwargs):
    """
    Puts the entire ingestion package together with a single call. This
    function uses the `fetch.fetch_all` and `wrangle.wrangle` methods in a
    callback chain to accomplish its work.

    Note: all work is logged in the database as an IngestionRecord.

    :param kwargs: should be the keyword arguments to `fetch_all`
    """

    startyear = int(kwargs.get('startyear', Config.STARTYEAR))
    endyear   = int(kwargs.get('endyear', Config.STARTYEAR))
    title     = kwargs.pop("title", "ELMR Ingestion Library")

    ## Create the log record
    log  = IngestionRecord(
        title=title,
        version=elmr.get_version(),
        start_year=date(startyear, 1, 1),
        end_year=date(endyear, 1, 1),
        duration=0.0,
        started=datetime.now(),
    )
    elmr.db.session.add(log)
    elmr.db.session.commit()

    ## Initiate the callback chain
    kwargs['callback'] = wrangle.wrangle
    duration, num_series, num_rows = fetch.fetch_all(**kwargs)

    ## Update the log record
    log.duration    = duration
    log.finished    = datetime.now()
    log.num_series  = num_series
    log.num_added   = num_rows[0]
    log.num_fetched = num_rows[1]
    elmr.db.session.commit()

    return log

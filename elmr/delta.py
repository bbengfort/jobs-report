# elmr.delta
# Compute rates of changes in time series
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue May 05 02:32:22 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: delta.py [] benjamin@bengfort.com $

"""
Compute rates of changes in time series by creating new timeseries that are
linked to the old time series, which expresses the delta. Precomputation
creates more data in the database, but makes faster computation.
"""

##########################################################################
## Imports
##########################################################################

from elmr import db
from elmr.models import Series, SeriesRecord

##########################################################################
## Functions
##########################################################################


def percent_change(records):
    """
    Expects an iterable of floats, returns the percent change for each
    record compared to the previous record. This function returns a list that
    is of length one shorter than the original records -- there is no change
    for the first item in the list.
    """
    last_value = None
    for record in records:
        if last_value is None:
            last_value = record
            continue

        yield (((record - last_value) / record) * 100)


def deltas(blsids=None, all=False, delete=True):
    """
    Handles string input (e.g. from the command line) to sync one ore more
    specific BLS IDs (str or int) or if all is True, then just does all of the
    series that are currently in the database. Basically this is the handler
    to call `compute_delta` many times.
    """

    if isinstance(blsids, basestring) or isinstance(blsids, int):
        # Convert blsids from a single id to a list of ids
        blsids = [blsids]

    if blsids is None and all:
        blsids = [s.id for s in Series.query.all()]

    if blsids is None and not all:
        raise ValueError("specify series ids or all")

    return [compute_delta(s, delete=delete) for s in blsids]


def compute_delta(series, delete=True):
    """
    For a single series computes the delta series. If the delta series exists
    the function attempts to update it. If `delete` is True, then the
    function starts over from scratch and deletes the original series. If no
    delta series exists, this function creates it.
    """

    if isinstance(series, basestring):
        # if the series is a string then it's a BLSID
        series = Series.query.filter_by(blsid=series).first()

    if isinstance(series, int):
        # if the series is an int then it's a series id
        series = Series.query.get(series)

    if not isinstance(series, Series):
        raise ValueError("Pass a blsid, an id, or a series object")

    if series.delta is not None:
        if delete:
            db.session.delete(series.delta)
            db.session.flush()
        else:
            raise NotImplementedError("Cannot handle existing delta series")

    if series.delta is None:

        delta = Series(**{
            "blsid": series.blsid + "-DELTA",
            "title": series.title + " [percent change]",
            "source": series.source + "-ANALYSIS",
            "is_primary": False,
            "is_delta": True,
            "is_adjusted": True if series.is_adjusted else False,
        })

        db.session.add(delta)
        series.delta = delta
        db.session.flush()

        last_value = None
        for record in series.records.order_by('period'):
            if last_value is None:
                last_value = record.value
                continue

            delta_record = SeriesRecord(**{
                "series": delta,
                "period": record.period,
                "value": ((record.value - last_value) / record.value) * 100,
                "footnote": None,
            })
            db.session.add(delta_record)

    db.session.commit()
    return delta

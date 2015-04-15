#!/usr/bin/env python
# elmr.fips
# Helper methods for FIPS codes and extracting FIPS info from the database.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue Apr 14 08:48:18 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: fips.py [] benjamin@bengfort.com $

"""
Helper methods for FIPS codes and extracting FIPS info from the database.
"""

##########################################################################
## Imports
##########################################################################

import re
import csv
import elmr

from datetime import date
from elmr.models import USAState, Series, StateSeries

##########################################################################
## Compiled Regex
##########################################################################

## Used for parsing the Series titles of LAUS and CESSM datasets
LAUSTRE = re.compile(r'^([\w\s]+),\s+([\w\s]+)\s+\-\s+([\w\s]+$)', re.I)
CESSMRE = re.compile(r'^([\w\s]+),\s+([\w\s,\-]+),\s+([\w\s]+)\s+\-\s+([\w\s]+$)', re.I)

##########################################################################
## Per-State CSV Data Set Generators
##########################################################################


def write_states_dataset(fobj, source, dataset, adjusted=True):
    """
    Writes a geographic csv of the series to the open file-like object passed
    in as `fobj`. Each row is an individual state, and each column is the
    period for the series. You may also specify seasonally adjusted with the
    `adjusted` boolean.

    The source can be either "LAUS" or "CESSM". If the source is "LAUS" then
    the dataset is expected to be one of:

        - employment
        - unemployment
        - labor force
        - unemployment rate

    If the source is "CESSM" then the data set is expected to be one of:

        - Total Nonfarm
        - Other Services
        - Information
        - Leisure and Hospitality
        - Mining, Logging, and Construction
        - Durable Goods
        - Transportation, Warehousing, and Utilities
        - Financial Activities
        - Trade, Transportation, and Utilities
        - Manufacturing
        - Construction
        - Mining and Logging
        - Education and Health Services
        - Non-Durable Goods
        - Professional and Business Services
        - Government

    This will write in place to the fobj that is passed to it.
    """

    fields = ["fips", "State"]

    ## TODO: Somehow get this from the database, not hardcoded logic.
    for year in xrange(2000, 2016):
        for month in xrange(1, 13):
            if year == 2015 and month > 3:
                break
            fields.append(date(year, month, 1).strftime("%b %Y"))

    # Create the CSV writer
    writer = csv.DictWriter(fobj, fieldnames=fields)
    writer.writeheader()

    # Create the database query - note, there is no checking
    for state in USAState.query.order_by('name'):
        ss = state.series.filter_by(adjusted=adjusted, source=source)
        if source == "CESSM":
            ss = ss.filter_by(category=dataset)
        elif source == "LAUS":
            ss = ss.filter_by(dataset=dataset)

        ss = ss.first()  # TODO: Check to make sure this returns a single result

        row = {
            "fips": state.fips,
            "State": state.name,
        }

        for record in ss.series.records:
            row[record.period.strftime("%b %Y")] = record.value

        writer.writerow(row)


##########################################################################
## Helper functions for data management
##########################################################################


def get_fips_codes(include_dc=False):
    """
    Generator that returns FIPS codes for the 50 U.S. States, skipping over
    codes for territories (and the District of Columbia). Codes are returned
    in order of state alphabetical order.
    """
    skipidx = {3, 7, 11, 14, 43, 52}
    if include_dc:
        skipidx.remove(11)

    for idx in xrange(1, 57):
        if idx not in skipidx:
            yield "US%02i" % idx


def get_conus_states(include_dc=False):
    """
    Returns an alphabetical list of States from the database, excluding
    territories (and the District of Columbia) to match FIPS codes.
    """
    query   = "SELECT title FROM series WHERE source IN ('LAUS', 'CESSM')"
    result  = elmr.db.session.execute(query)
    states  = set([parse_series_title(row[0])['state'] for row in result])

    exclude = {u'Puerto Rico', u'Virgin Islands'}
    if not include_dc:
        exclude.add(u'District of Columbia')

    conus   = states - exclude
    return sorted(conus)


def parse_series_title(title):
    """
    Extracts the state, the seasonality, the dataset and the category from
    a title of a series from either the LAUS or CESSM sources.
    """

    def is_adjusted(s):
        """
        String matching for seasonality
        """
        s = s.lower().strip()
        if s == "seasonally adjusted":
            return True
        elif s == "not seasonally adjusted":
            return False
        else:
            raise ValueError(
                "Could not determine seasonality from '%s'" % s
            )

    match = None
    for regex in (LAUSTRE, CESSMRE):
        match = regex.match(title)
        if match is not None:
            break

    if match is None:
        raise ValueError(
            "Could not parse '%s' as LAUS or CESSM title" % title
        )

    groups = list(match.groups())
    if len(groups) == 3:
        # Insert None value at second position
        groups.insert(1, None)

    # Handle seasonality
    groups[2] = is_adjusted(groups[2])

    fields = ("state", "category", "adjusted", "dataset")
    return dict(zip(fields, groups))


def get_state_series_info(source="both"):
    """
    Returns a dictionary of state series information for use in dumping related
    records to a CSV file or to create SQL migrations.
    """

    source_jump = {
        "both": "('LAUS', 'CESSM')",
        "laus": "('LAUS')",
        "cessm": "('CESSM')",
    }

    source = source.lower()
    if source not in source_jump:
        raise ValueError(
            "'%s' not a valid source, use %s"
            % (source, ", ".join(source_jump.keys()))
        )

    pred = source_jump[source]
    query = "SELECT blsid, title, source FROM series WHERE source IN %s" % pred

    for blsid, title, source in elmr.db.session.execute(query):
        row = parse_series_title(title)
        row["blsid"]  = blsid
        row["source"] = source

        yield row


def dump_state_series(path="state_series.csv", source="both"):
    """
    Dumps a CSV file with the series information for each state and state
    information such as the FIPS code, for use in information processing.
    """

    fieldnames = (
        "state", "blsid", "adjusted", "dataset", "source", "category"
    )

    with open(path, "w") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in get_state_series_info(source):
            writer.writerow(row)

if __name__ == '__main__':
    dump_state_series()

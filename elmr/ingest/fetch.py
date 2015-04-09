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
stores it in a Fixtures directory for wrangling.
"""

##########################################################################
## Imports
##########################################################################

import os
import json
import datetime

from elmr.config import Config
from elmr.ingest.blsapi import bls_series

##########################################################################
## Module Constants
##########################################################################

STARTYEAR  = Config.STARTYEAR   # Fetch start
ENDYEAR    = Config.ENDYEAR     # Fetch end
FIXTURES   = Config.FIXTURES    # Fixtures directory

TimeSeries = {
    "LNS11000000": "Civilian Labor Force Level",
    "LNS11300000": "Civilian Labor Force Participation Rate",
    "LNS12000000": "Employment Level",
    "LNS12300000": "Employment-Population Ratio",
    "LNS12500000": "Employed, Usually Work Full Time",
    "LNS12600000": "Employed, Usually Work Part Time",
    "LNS13000000": "Unemployment Level",
    "LNS14000000": "Unemployment Rate",
    "LNS14000012": "Unemployment Rate - 16-19 Years",
    "LNS14000025": "Unemployment Rate - 20 Years & Over Men",
    "LNS14000026": "Unemployment Rate - 20 Years & Over Women",
    "LNS14000003": "Unemployment Rate - White",
    "LNS14000006": "Unemployment Rate - Black or African American",
    "LNS14032183": "Unemployment Rate - Asian",
    "LNS14000009": "Unemployment Rate - Hispanic or Latino",
    "LNS14027659": "Unemployment Rate - 25 Years & Over, Less than a High School Diploma",
    "LNS14027660": "Unemployment Rate - 25 Years & Over, High School Graduates No College",
    "LNS14027689": "Unemployment Rate - 25 Years & Over, Some College or Associate Degree",
    "LNS14027662": "Unemployment Rate - 25 Years & Over, Bachelor's Degree and Higher",
    "LNS13008396": "Number Unemployed For Less Than 5 weeks",
    "LNS13008756": "Number Unemployed For 5-14 Weeks",
    "LNS13008516": "Number Unemployed For 15 Weeks & Over",
    "LNS13008636": "Number Unemployed For 27 Weeks & Over",
    "LNS13008275": "Average Weeks Unemployed",
    "LNS13008276": "Median Weeks Unemployed",
    "LNS13023621": "Unemployment Level Job Losers",
    "LNS13023653": "Unemployment Level Job Losers On Layoff",
    "LNS13025699": "Unemployment Level Job Losers Not on Layoff",
    "LNS13023705": "Unemployment Level Job Leavers",
    "LNS13023557": "Unemployment Level Reentrants To Labor Force",
    "LNS13023569": "Unemployment Level New Entrants",
    "LNS12032194": "Persons At Work Part Time for Economic Reasons",
    "LNS15000000": "Not in Labor Force",
    "LNU05026642": "Marginally Attached to Labor Force",
    "LNU05026645": "Discouraged Workers",
    "LNS13327709": "Alternative measure of labor underutilization U-6",
    "LNS12026619": "Multiple Jobholders Level",
    "LNS12026620": "Multiple Jobholders as a Percent of Total Employed",
    "LNU02036012": "Employment Level, Nonag. Industries, With a Job not at Work, Bad Weather",
    "LNU02033224": "Employment Level, Nonag. Industries, At Work 1-34 Hrs, Usually Work Full time, Bad Weather",
}


def fetch_all(startyear=STARTYEAR, endyear=ENDYEAR, fixtures=FIXTURES):
    dname  = "ingest-%s" % datetime.datetime.now().strftime("%Y-%m-%d")
    folder = os.path.join(fixtures, dname)

    if not os.path.exists(folder):
        os.makedirs(folder)

    for idx in xrange(0, len(TimeSeries), 10):
        series = TimeSeries.keys()[idx:idx + 10]
        data   = bls_series(series, startyear=STARTYEAR, endyear=ENDYEAR)

        for dataset in data['Results']['series']:
            fname = os.path.join(folder, "%s.json" % dataset['seriesID'])
            with open(fname, 'w') as f:
                json.dump(dataset, f, indent=2)

    return folder, len(TimeSeries)

##########################################################################
## Main Method
##########################################################################

if __name__ == '__main__':
    fetch_all()

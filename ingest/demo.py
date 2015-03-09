# ingest.demo
# Code snippet showing how to download TimeSeries data using the BLS API.
#
# Author:   Benjamin Bengfort <bengfort@cs.umd.edu>
# Created:  Mon Mar 09 16:02:00 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: demo.py [] bengfort@cs.umd.edu $

"""
Code snippet showing how to download TimeSeries data using the BLS API.
"""

##########################################################################
## Imports
##########################################################################

import os
import json
import requests
import prettytable

##########################################################################
## Module Constants
##########################################################################

## Status messages from BLS API
REQUEST_SUCCEEDED = u'REQUEST_SUCCEEDED'
REQUEST_FAILED    = u'REQUEST_FAILED'

## Fetch the BLS API Key from the environment
BLS_API_KEY  = os.environ.get('BLS_API_KEY')

## BLS API Endpoint
BLS_ENDPOINT = "http://api.bls.gov/publicAPI/v2/timeseries/data/"

def single_series(series_id, **kwargs):
    """
    Used to fetch data for a single timeseries ID for the past three years.
    Pass in a single series id (a string) as an argument.
    """
    endpoint = BLS_ENDPOINT + series_id
    headers  = kwargs.get("headers", {})
    response = requests.get(endpoint, headers=headers)


    if response.status_code != requests.codes.ok:
        response.raise_for_status()

    return response.json()

def multiple_series(series_id, **kwargs):
    """
    Used to fetch data for up to 25 timeseries IDs for the past three years.
    Pass in a list of series_ids to fetch them all (if you pass in a single
    string, this method will defer to the single_series method).
    """
    if isinstance(series_id, basestring):
        return single_series(series_id, **kwargs)

    if not isinstance(series_id, list):
        raise TypeError("Pass in a string or a list as a series_id")

    if len(series_id) < 1 or len(series_id) > 25:
        raise ValueError("Must pass in between 1 and 25 series ids")

    headers  = {'Content-Type': 'application/json'}
    headers.update(kwargs.get('headers', {}))

    payload  = kwargs.get('payload', {})
    payload.update({'seriesid': series_id})

    response = requests.post(BLS_ENDPOINT, data=json.dumps(payload), headers=headers)

    if response.status_code != requests.codes.ok:
        response.raise_for_status()

    result   = response.json()
    if result['status'] == REQUEST_FAILED:
        raise Exception(result['message'][0])

    return result

def bls_series(series_id, **kwargs):
    """
    Authenticated request to the BLS API to fetch timeseries data in JSON
    form. You can pass a list of up to 25 series_ids to fetch multiple
    series, or you can pass in a single series_id string to do a simple
    request. You can also pass in parameters via the kwargs:

        - startyear (4 digit year)
        - endyear (4 digit year)
        - catalog (True or False)
        - calculations (True or False)
        - annualaverage (True or False)
        - registrationKey (api key from BLS website)
    """

    # Convert strings to a list for authentication
    if isinstance(series_id, basestring):
        series_id = [series_id,]

    headers  = kwargs.pop('headers', {})
    payload  = {'registrationKey': BLS_API_KEY}
    payload.update(kwargs)

    return multiple_series(series_id, headers=headers, payload=payload)

##########################################################################
## Main Statement with Demo code
##########################################################################

if __name__ == '__main__':

    ## Demo Series
    series = ['LNS12000000','LNS13000000', 'LNS10000000']
    result = bls_series(series, startyear='2010', endyear='2015')

    ## Pretty print a table of the results
    for s in result['Results']['series']:
        table = prettytable.PrettyTable(["series id","year","period","value","footnotes"])
        for item in s['data']:
            row   = [
                s['seriesID'],                  # Series ID
                item['year'],                   # Year
                item['period'],                 # Period
                item['value'],                  # Value
            ]

            # Footnotes
            row.append(", ".join([fn['text'] for fn in item['footnotes'] if 'text' in fn]))

            table.add_row(row)

        print table.get_string()

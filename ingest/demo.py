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

import prettytable

from blsapi import *

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

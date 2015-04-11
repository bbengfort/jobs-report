#!/usr/bin/env python
# scraper
# This simple script scrapes the BLS website for Series IDs
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  codetime
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: scraper.py [] benjamin@bengfort.com $

"""
This simple script scrapes the BLS website for Series IDs

WARNING: This script is not intended for use, it is provided for reference as
the manner in which Ben downloaded the initial BLS Series IDs to begin the
ingestion process. Please don't use this unless you know what you're doing!
"""

##########################################################################
## Imports
##########################################################################

import os
import sys
import bs4
import json
import requests

##########################################################################
## Module Constants
##########################################################################

## Important Paths
ADMN_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.normpath(os.path.join(ADMN_DIR, ".."))
FIXTURES = os.path.join(BASE_DIR, "fixtures")

CPS_URL  = "http://data.bls.gov/cgi-bin/surveymost?ln"
CES_URL  = "http://data.bls.gov/cgi-bin/surveymost?ce"
CESM_URL = "http://data.bls.gov/cgi-bin/surveymost?sm"
LAUS_URL = "http://data.bls.gov/cgi-bin/surveymost?la"

##########################################################################
## Helper Methods
##########################################################################


def scrape_standard(url, name):
    """
    Scrapes and wrangles the CPS most popular time series ids.

    Adapted to handle any regular list.
    """

    print "Beginning Ingestion of %s IDs" % name
    series   = {}
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Could not fetch %s time series page" % name)

    soup = bs4.BeautifulSoup(response.content, 'lxml')
    for dd in soup.find_all('dd'):
        key = dd.input.attrs['value']
        val = dd.get_text().split("\n")[0].rsplit("-", 1)[0].strip()

        series[key] = val

    print "Fetched %i %s Series IDs" % (len(series), name)
    return series


def scrape_states(url, name):
    """
    Scrapes time series for each state in the LAUS most popular list

    Adapted to handle any state list.
    """

    def scrape_laus_state(url, state, name=name):
        """
        Inner method for each LAUS state
        """
        series   = {}
        response = requests.get(url)
        fields   = (
            "labor force",
            "employment",
            "unemployment",
            "unemployment rate",
        )

        if response.status_code != 200:
            raise Exception("Could not fetch state %s time series page" % name)

        soup = bs4.BeautifulSoup(response.content, 'lxml')
        for dd in soup.find_all('dd'):
            keys = dd.input.attrs['value']
            name = dd.get_text().split("\n")[0].rsplit("-", 1)[0].strip()

            if name.startswith(state + ","):
                for idx, key in enumerate(keys.split(",")):
                    key = key.strip()
                    val = "%s - %s" % (name, fields[idx])
                    series[key] = val

        return series

    print "Beginning Ingestion of %s IDs" % name
    series   = {}
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Could not fetch %s time series page" % name)

    soup = bs4.BeautifulSoup(response.content, 'lxml')
    for li in soup.select('#bodytext ul li'):
        key = li.a.get_text().strip()
        url = li.a.attrs['href']
        val = scrape_laus_state(url, key)

        series[key] = val

    print "Fetched %i %s Series IDs" % (len(series), name)
    return series

##########################################################################
## Main Method
##########################################################################

if __name__ == '__main__':

    print "Warning: this script was not intended for regular use!"
    if raw_input("Continue? [Y/n] ") != "Y":
        sys.exit(0)

    ## Data storage
    series   = {}

    ## Ingest CPS Series IDs
    series['CPS']  = scrape_standard(CPS_URL, "CPS")

    ## Ingest CES Series IDs
    series['CESN'] = scrape_standard(CES_URL, "CES")

    ## Ingest CES State and Metro IDs
    series['CESSM'] = scrape_states(CESM_URL, "CESSM")

    ## Ingest LAUS Series IDs
    series['LAUS'] = scrape_states(LAUS_URL, "LAUS")

    ## Dump the scraped data to disk
    path = os.path.join(FIXTURES, "seriesids.json")
    with open(path, 'w') as f:
        json.dump(series, f, indent=2)

    print "data written to %s" % path

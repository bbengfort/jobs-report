#!/usr/bin/env python

# elmer-admin
# Script for executing ELMR related management commands
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Apr 06 15:35:03 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: elmer-admin.py [] benjamin@bengfort.com $

"""
Script for executing ELMR related management commands
"""

##########################################################################
## Imports
##########################################################################

import os
import sys
import argparse

## Important Paths
ADMN_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.normpath(os.path.join(ADMN_DIR, ".."))
FIXTURES = os.path.join(BASE_DIR, "fixtures")

## Auto adapt Python path
sys.path.append(BASE_DIR)

## Import ELMR Libraries
import elmr

from elmr.config import get_settings_object
from ingest import fetch, wrangle

##########################################################################
## Script Definition
##########################################################################

DESCRIPTION = "An administrative utility for the ELMR Project"
EPILOG      = "If there are any bugs or concerns, submit an issue on Github"
VERSION     = elmr.get_version()

##########################################################################
## Commands
##########################################################################


def runserver(args):
    """
    Run the local development server
    """
    mode = get_settings_object("development")
    print "running ELMR with %s configuration" % mode

    elmr.app.run()
    return ""


def ingest_data(args):
    """
    Ingest and wrangle data from BLS
    """
    fetchopts = {
        "fixtures": FIXTURES,
        "startyear": args.start_year or fetch.STARTYEAR,
        "endyear": args.end_year or fetch.ENDYEAR
    }

    folder, num_series = fetch.fetch_all(**fetchopts)

    fcsv, num_rows = wrangle.wrangle_csv()
    fjson, _ = wrangle.wrangle_json()

    return (
        "Ingested %i rows in %i time series to %s\n"
        "Wrote JSON data to %s\n"
        "Wrote CSV data to %s"
    ) % (num_rows, num_series, folder, fcsv, fjson)

##########################################################################
## Main method and command entry point
##########################################################################

if __name__ == '__main__':

    # Construct the argument parser
    parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=EPILOG, version=VERSION)
    subparsers = parser.add_subparsers(title='commands', description='Administrative commands for ELMR')

    # Run Server Command
    server_parser = subparsers.add_parser('runserver', help='Run local development server')
    server_parser.set_defaults(func=runserver)

    # Ingest Command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest and wrangle data from BLS')
    ingest_parser.add_argument('--start-year', metavar="YEAR", default=None, help="starting year of timeseries to ingest")
    ingest_parser.add_argument('--end-year', metavar="YEAR", default=None, help="ending year of timeseries to ingest")
    ingest_parser.set_defaults(func=ingest_data)

    # Handle input from the command line
    args = parser.parse_args()            # Parse the arguments
    try:
        msg = args.func(args)             # Call the default function
        parser.exit(0, msg + "\n")        # Exit cleanly with message
    except Exception as e:
        parser.error(str(e))              # Exit with error

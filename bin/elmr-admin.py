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
import imp
import argparse
import importlib

## Imports for database handling
from migrate.versioning import api

## Important Paths
ADMN_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.normpath(os.path.join(ADMN_DIR, ".."))
FIXTURES = os.path.join(BASE_DIR, "fixtures")

## Auto adapt Python path
sys.path.append(BASE_DIR)

## Import ELMR Libraries
import elmr

from elmr.ingest import ingest
from elmr.config import get_settings_object
from elmr.delta import deltas

##########################################################################
## Script Definition
##########################################################################

DESCRIPTION = "An administrative utility for the ELMR Project"
EPILOG      = "If there are any bugs or concerns, submit an issue on Github"
VERSION     = elmr.get_version()

##########################################################################
## Helper functions
##########################################################################


def get_config(mode="development"):
    """
    Perform dynamic loading of Config just like Flask!
    """
    name = get_settings_object(mode)
    mod, cls = name.rsplit(".", 1)
    module = importlib.import_module(mod)
    return getattr(module, cls)

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

    conf = get_config()
    opts = dict(vars(args))
    del opts['func']

    opts['startyear'] = opts.pop('start_year') or conf.STARTYEAR
    opts['endyear']   = opts.pop('end_year') or conf.ENDYEAR

    record = ingest(**opts)

    return (
        "Ingested %i rows in %i time series in %0.3f seconds"
    ) % (record.num_added, record.num_series, record.duration)


def compute_deltas(args):
    """
    After ingestion, compute the delta series
    """

    if args.all:
        series = deltas(None, all=True, delete=args.delete)
    elif len(args.blsid) > 0:
        series = deltas(args.blsid, delete=args.delete)
    else:
        return "No BLSIDs specified, use --all or specify them"

    output = ["Computed deltas for %d series:" % len(series)]
    for s in series:
        output.append("%s syncs %s with %d records"
                      % (s.blsid, s.original.first().blsid,
                         s.records.count()))
    output.append("")
    return "\n".join(output)


def createdb(args):
    """
    Creates the migrations repository and the database
    """

    # Get the configruation
    config = get_config()

    # Execute CREATE TABLE statements
    elmr.db.create_all()

    # Store version control and migrations
    if not os.path.exists(config.MIGRATIONS):
        api.create(config.MIGRATIONS, 'elmr_db_repo')
        api.version_control(config.DATABASE_URI, config.MIGRATIONS)
    else:
        api.version_control(
            config.DATABASE_URI,
            config.MIGRATIONS,
            api.version(config.MIGRATIONS),
        )

    return "Database created, migrations at %s" % config.MIGRATIONS


def migrate(args):
    """
    Create DB migrations for current version
    """

    # Get the configruation
    config = get_config()
    DB_URI = config.DATABASE_URI
    M_REPO = config.MIGRATIONS

    v = api.db_version(DB_URI, M_REPO)
    m = os.path.join(M_REPO, 'versions', '%03d_migration.py' % (v + 1))

    tmpmod = imp.new_module('old_model')
    oldmod = api.create_model(DB_URI, M_REPO)
    exec(oldmod, tmpmod.__dict__)

    script = api.make_update_script_for_model(
        DB_URI, M_REPO, tmpmod.meta, elmr.db.metadata
    )

    with open(m, 'wt') as f:
        f.write(script)

    v = api.db_version(DB_URI, M_REPO)

    return "New migration saved as %s\nCurrent database version: %d" % (m, v)


def upgrade(args):
    """
    Runs the database upgrade migration script (run migrate first)
    """

    # Get the configruation
    config = get_config()
    DB_URI = config.DATABASE_URI
    M_REPO = config.MIGRATIONS

    api.upgrade(DB_URI, M_REPO)
    v = api.db_version(DB_URI, M_REPO)
    return "Current database version: %i" % v


def downgrade(args):
    """
    Restores the database one previous version, run multiple times to go
    back multiple versions if needed.
    """

    # Get the configruation
    config = get_config()
    DB_URI = config.DATABASE_URI
    M_REPO = config.MIGRATIONS

    v = api.db_version(DB_URI, M_REPO)
    api.downgrade(DB_URI, M_REPO, v - 1)
    v = api.db_version(DB_URI, M_REPO)
    return "Current database version: %i" % v

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
    ingest_parser.add_argument('--fixtures', default=FIXTURES, metavar='PATH', help="root dir to store downloads")
    ingest_parser.add_argument('--start-year', metavar="YEAR", default=None, help="starting year of timeseries to ingest")
    ingest_parser.add_argument('--end-year', metavar="YEAR", default=None, help="ending year of timeseries to ingest")
    ingest_parser.add_argument('--cleanup', action="store_true", help="remove temporary disk storage when done")
    ingest_parser.add_argument('--per-page', dest='blocksize', type=int, default=10, help="number of series to fetch from the api at at time")
    ingest_parser.add_argument('--wait', dest='ratelimit', metavar='SEC', default=1, type=int, help="seconds to wait between API calls")
    ingest_parser.add_argument('--title', metavar='TEXT', default="ELMR Command Line Ingestion", help="specify a title for the ingestion record")
    ingest_parser.set_defaults(func=ingest_data)

    # Compute Deltas Command
    deltas_parser = subparsers.add_parser('deltas', help='Compute deltas for all or a single series.')
    deltas_parser.add_argument('--all', action="store_true", help="compute deltas for all series, not just one")
    deltas_parser.add_argument('--delete', action="store_true", help="force a recomputation of the entire delta series")
    deltas_parser.add_argument('blsid', type=unicode, nargs="*", help='bls series ids to compute the deltas for')
    deltas_parser.set_defaults(func=compute_deltas)


    # CreateDB Command
    createdb_parser = subparsers.add_parser('createdb', help='Create database and migrations')
    createdb_parser.set_defaults(func=createdb)

    # Migrate Command
    migrate_parser = subparsers.add_parser('migrate', help='Create DB migrations for current version')
    migrate_parser.set_defaults(func=migrate)

    # Upgrade Command
    upgrade_parser = subparsers.add_parser('upgrade', help='Run DB migrations for next version')
    upgrade_parser.set_defaults(func=upgrade)

    # Downgrade Command
    downgrade_parser = subparsers.add_parser('downgrade', help='Downgrade DB to previous version')
    downgrade_parser.set_defaults(func=downgrade)

    # Handle input from the command line
    args = parser.parse_args()            # Parse the arguments
    try:
        msg = args.func(args)             # Call the default function
        parser.exit(0, msg + "\n")        # Exit cleanly with message
    except Exception as e:
        parser.error(str(e))              # Exit with error

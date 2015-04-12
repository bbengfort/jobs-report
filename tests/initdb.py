# tests.initdb
# Helper functions for initializing the test database and loading fixtures.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Apr 12 12:47:41 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: initdb.py [] benjamin@bengfort.com $

"""
Helper functions for initializing the test database and loading fixtures.
"""

##########################################################################
## Imports
##########################################################################

import re
import os
import elmr
import psycopg2

##########################################################################
## Module Variables
##########################################################################

## Import for fixtures
TESTDIR  = os.path.dirname(__file__)
FIXTURES = os.path.normpath(os.path.join(TESTDIR, "..", "fixtures"))
TESTDATA = os.path.join(FIXTURES, "testset")

## Fixtures for the database
RECORDS_FIXTURE    = os.path.join(TESTDATA, "records.csv")
SERIES_FIXTURE     = os.path.join(TESTDATA, "series.csv")
INGESTIONS_FIXTURE = os.path.join(TESTDATA, "ingestions.csv")

## Compiled regular expressions
DBURI_REGEX = re.compile(
    r'^postgresql\+psycopg2:\/\/(?P<U>.+):(?P<P>.+)@(?P<H>.+)/(?P<D>.+)$',
    re.I
)

##########################################################################
## Database Helper Functions
##########################################################################


def syncdb():
    """
    Creates all the tables in the database. Wrapper for `elmr.db.create_all`.
    """
    elmr.db.create_all()


def loaddb(**kwargs):
    """
    Loads all the fixtures from the CSV file into the databaase. Can specify
    only some of the fixtures by setting the table flags in the arguments, by
    default this function will load all fixtures. For example, to load only
    the series and the ingestions, pass ass follows:

        loaddb(ingestions=True, series=True, records=False)

    If a keyword argument is ommitted, it's assumed to be True.
    Exceptions are not captured - they are passed on!
    """

    # TABLENAME: FIXTUREPATH
    fixtures = {
        "ingestions": INGESTIONS_FIXTURE,
        "series": SERIES_FIXTURE,
        "records": RECORDS_FIXTURE,
    }

    # Connect directly to PostgreSQL
    connection = psycopg2.connect(parse_dburi())

    for table, fixture in fixtures.items():
        if kwargs.get(table, True):
            load_fixture(connection, table, fixture)

    connection.close()


def dropdb():
    """
    Drops all of the tables and data in the database, readying it for refresh
    between tests - to ensure each test happens in isolation.
    """
    elmr.db.session.remove()
    elmr.db.drop_all()


def parse_dburi(dburi=None):
    """
    Parses the SQLAlchemy DATABASE_URI and returns a psycopg2 dsn connection
    string in order to make direct connections with PostgreSQL.
    """

    if dburi is None:
        dburi = elmr.app.config["DATABASE_URI"]

    match = DBURI_REGEX.match(dburi)
    if match is None:
        raise ValueError(
            "Could not parse DATABASE URI: '%s' is invalid" % dburi
        )

    value = match.groupdict()

    dsn = "dbname=%(D)s user=%(U)s password=%(P)s host=%(H)s port=5432"
    return dsn % value


def load_fixture(conn, table, path):
    """
    Given a connection to a database (e.g. a straight up psycopg2 connection),
    this function will open a CSV file at path, and dump it to PostgreSQL via
    the `copy_expert` command.
    """

    COPY_SQL = """
        COPY %s FROM STDIN WITH
            CSV
            HEADER
            DELIMITER AS ','
        """

    with open(path, 'r') as f:
        cursor = conn.cursor()
        cursor.copy_expert(sql=COPY_SQL % table, file=f)
        conn.commit()
        cursor.close()

#!/usr/bin/env python

import os
import re
import sys
import json
import psycopg2

BASE_PATH  = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
FIXTURES   = os.path.join(BASE_PATH, "fixtures")
MIGRATIONS = os.path.join(BASE_PATH, "elmr", "migrations", "versions")

## Auto adapt Python path
sys.path.append(BASE_PATH)

## Import ELMR Libraries
import elmr

from elmr.utils import slugify
from collections import defaultdict
from datetime import datetime

## Compiled regular expressions
DBURI_REGEX = re.compile(
    r'^postgresql\+psycopg2:\/\/(?P<U>.+):(?P<P>.+)@(?P<H>.+)/(?P<D>.+)$',
    re.I
)


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


def load_mapping(fixture="mapping.json"):
    with open(os.path.join(FIXTURES, fixture), 'r') as f:
        description = json.load(f)
        mapping = defaultdict(dict)
        for d in description:
            original = d['original']
            actual   = d['actual']

            mapping[original]['name'] = actual
            mapping[original]['slug'] = slugify(actual)

    return mapping


def get_migration_file(upgrade=True):
    name = "006_tsrename_postgresql_%s.sql"
    name = name % "upgrade" if upgrade else name % "downgrade"
    return os.path.join(MIGRATIONS, name)


def get_series_records(table="series"):

    sql = {
        "series": "SELECT * FROM series WHERE source='LAUS'",
        "states_series": "SELECT * FROM states_series WHERE source='LAUS'"
    }[table]

    conn = psycopg2.connect(parse_dburi())
    cursor = conn.cursor()
    cursor.execute(sql)

    for row in cursor.fetchall():
        yield row

    cursor.close()
    conn.close()


def make_migrations(mapping, upgrade_path, downgrade_path):

    with open(upgrade_path, 'w') as upsql:
        with open(downgrade_path, 'w') as downsql:

            # Write out the HEADER statements
            header = (
                "--\n"
                "-- %%s script for name snafoo fix\n"
                "-- Fixes the scraping naming snafoo by updating rows in "
                "states and states_series\n"
                "-- Created: %s\n"
                "--\n\n"
            ) % datetime.now().strftime("%c")

            upsql.write(header % "Upgrade")
            downsql.write(header % "Downgrade")

            # Write out the BEGIN statements
            upsql.write("BEGIN;\n\n")
            downsql.write("BEGIN;\n\n")

            # Deal with the series table
            upsql.write("-- UPDATE series.title according to the re-mappings\n")
            downsql.write("-- UPDATE series.title back to the pre-mapping titles\n")

            for row in get_series_records(table="series"):
                sid  = row[0]
                orig = row[2]
                rsql = "UPDATE series SET title='%s' WHERE id=%d;\n"
                dsql = rsql % (orig, sid)

                parts = orig.rsplit("-", 1)
                parts[1] = " %s" % mapping[parts[1].strip()]['name']
                fixd = "-".join(parts)
                usql = rsql % (fixd, sid)

                downsql.write(dsql)
                upsql.write(usql)

            # Deal with the states series table
            upsql.write("\n\n-- UPDATE states_series dataset and slug according to re-mapping\n")
            downsql.write("\n\n-- UPDATE states_series dataset and slug back to the pre-mapping\n")

            for row in get_series_records(table="states_series"):
                rsql = "UPDATE states_series SET dataset='%s', slug='%s' WHERE id=%d;\n"
                sid  = row[0]
                ods  = row[4]
                osl  = row[7]

                downsql.write(rsql % (ods, osl, sid))

                nds  = mapping[ods]['name']
                nsl  = mapping[ods]['slug']

                upsql.write(rsql % (nds, nsl, sid))

            # Write out the COMMIT statements
            upsql.write("\n\nCOMMIT;\n")
            downsql.write("\n\nCOMMIT;\n")


if __name__ == '__main__':
    mapping = load_mapping()
    upgradesql = get_migration_file()
    downgradesql = get_migration_file(False)
    make_migrations(mapping, upgradesql, downgradesql)

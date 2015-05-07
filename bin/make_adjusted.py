#!/usr/bin/env python

up = """--
-- Upgrade to database version 009: more meta data on series table
-- Created: %s
--


BEGIN;

ALTER TABLE series
    ADD COLUMN delta_id integer,
    ADD COLUMN is_delta boolean NOT NULL DEFAULT FALSE,
    ADD COLUMN is_adjusted boolean NOT NULL DEFAULT FALSE;

ALTER TABLE series
    ADD CONSTRAINT delta_series_series_id_fkey
        FOREIGN KEY (delta_id)
        REFERENCES series(id)
    ON DELETE CASCADE;

"""

cm = "COMMIT;"

import os
import re
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime
from elmr.models import Series

uscript = os.path.join(
    os.path.dirname(__file__),
    "..", "elmr", "migrations", "versions",
    "009_deltas_postgresql_upgrade.sql"
)

isnot_adjust = re.compile(r'not\s+seasonally\s+adjusted', re.I)
is_adjust = re.compile(r'seasonally\s+adjusted', re.I)

updatesql = "UPDATE series SET is_adjusted='%s' WHERE id=%d;\n"

with open(uscript, 'w') as f:
    f.write(up % datetime.now().strftime('%c'))

    for series in Series.query.all():
        parts = series.title.rsplit("-", 1)
        parts = parts[0].rsplit(",", 1)
        seasonal = parts[-1].strip()

        sql = None
        if is_adjust.match(seasonal):
            sql = updatesql % ('t', series.id)
        elif isnot_adjust.match(seasonal):
            sql = updatesql % ('f', series.id)
        else:
            print ("Undetermined seasonality: Series %d: \"%s\""
                   % (series.id, series.title))
            # sql = updatesql % ('f', series.id)

        if sql:
            f.write(sql)

    f.write(cm)

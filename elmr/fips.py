#!/usr/bin/env python

import csv
import elmr


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


def dump_state_series(path="state_series.csv", adjusted=True):
    """
    Dumps a CSV file with the series information for each state and state
    information such as the FIPS code, for use in information processing.
    """

    datasets = [
        "unemployment rate",
        "unemployment",
        "employment",
        "labor force",
    ]

    if adjusted:
        ilike = "%%, seasonally adjusted - %s"
    else:
        ilike = "%%, not seasonally adjusted - %s"

    fieldnames = ('dataset', 'state', 'fips', 'blsid')

    with open(path, "w") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for ds in datasets:
            match = ilike % ds
            query = (
                "SELECT blsid, title FROM series "
                "WHERE title ILIKE '%s' AND source='LAUS'"
                "ORDER BY title"
            ) % match

            result = elmr.db.session.execute(query)
            fips   = list(get_fips_codes())

            idx    = 0
            for row in result:
                if 'Puerto Rico' in row[1]:
                    continue

                item = {
                    'dataset': ds,
                    'blsid': row[0],
                    'fips': fips[idx],
                    'state': row[1].split(",")[0],
                }

                writer.writerow(item)

                idx += 1

if __name__ == '__main__':
    dump_state_series()

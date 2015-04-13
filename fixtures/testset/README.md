# Test Data Set

The CSV files in this directory represent fixtures for test data. They will be loaded by the test harness at test time and are used both for integration testing on Travis and for local test databases (where you don't want to do a full ingestion). Loading them into an `elmrtest` database is easy with a few commands as follows:

```
$ psql -c "CREATE ROLE tester WITH LOGIN PASSWORD 'secret';"
$ psql -c "CREATE DATABASE elmrtest WITH OWNER tester"
$ ELMR_SETTINGS=testing python
>>> from tests.initdb import syncdb, loaddb
>>> syncdb()
>>> loaddb()
```

Be careful though: ensure that you are using ELMR_SETTINGS=testing, otherwise this will connect to whatever database you have configured, and load the records there!

For more on loading CSV data with Python (using psycopg2 and the COPY command): [Load a CSV File with Header in Postgres via Psycopg](http://www.laurivan.com/load-a-csv-file-with-header-in-postgres-via-psycopg/).

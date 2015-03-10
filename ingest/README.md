# Jobs Report Data Ingestion

This document describes how to perform data ingestion and wrangling using
the ingest code in this library to fetch data from the BLS API.

For more information see: [BLS Developers](http://www.bls.gov/developers/home.htm)

## Getting Started

In order to make authenticated requests to the BLS API, you need to first obtain an API key. Without the API key you will be allowed to request data for multiple series for the past three years. In order to parameterize your request and get additional data, you need the key.

To obtain the key, go to the [BLS Registration](http://data.bls.gov/registrationEngine/) page and fill out the form. They will email you the key (you'll also have to click on a link to validate your email). Once you have the key, you can use it in requests to the BLS API.

## Using the BLS API code

The Python module `blsapi` provides three functions for interacting with data on the BLS website:

- `single_series`: allows you to download a single time series for the past three years
- `multiple_series`: allows you to download multiple time series for the past three years
- `bls_series`: allows you to make authenticated, parameterized requests.

All of these methods require a TimeSeries code to work. Unfortunately, there is no index of TimeSeries ids on the BLS website, you'll have to find the ID from the page of the data set you're looking for. However, if you use the [Data Tools](http://www.bls.gov/data/) section of the BLS site, you can find what you're looking for. In particular, for the CPS data see the CSV file [ln.series](http://download.bls.gov/pub/time.series/ln/ln.series) which gives the IDs of various data. I've initially identified three timeseries of interest:

```python
series = [
    'LNS10000000', # Population Level
    'LNS12000000', # Employment Level
    'LNS13000000', # Unemployment Level
]
```

In order to download a single time series, with data for the past three years, simply use the function as follows:

```python
from blsapi import single_series
data = single_series('LNS10000000')
```

The data will be returned as a Python dictionary, loaded from the JSON response. Multiple series for the past three years is just as easy:

```python
from blsapi import mutiple_series
data = multiple_series(['LNS10000000', 'LNS12000000', 'LNS13000000'])
```

Just pass in a list of series ids that you wish to fetch. Note that you have to pass at least 1 time series, and no more than 25 time series.

However, for the most part you want to perform **authenticated requests**. You do this by sending in your API key with every request. By doing this you can access more data than just the past three years, and parameterize your request with various arguments. There are two ways that the `blsapi` will find your API key:

1. Store it as an environment variable, `BLS_API_KEY`.
2. Pass it in to the function as `registrationKey`.

If you'd like to use the environment variable, in your terminal type:

```bash
$ export BLS_API_KEY=yourkey
```

Then in Python:

```python
from blsapi import bls_series
data = bls_series(series, endyear="2010", startyear="2000")
```

This function can fetch data for 1 to 25 timeseries that you pass into it. The parameters that you can pass in are as follows:

- `startyear` (4 digit year as a string)
- `endyear` (4 digit year as a string)
- `catalog` (True or False)
- `calculations` (True or False)
- `annualaverage` (True or False)
- `registrationKey` (api key from BLS website)

For example, to fetch the data and pretty print it as a table:

```python
import prettytable

from blsapi import *

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
```

Hope this helps you get started using the BLS API data!

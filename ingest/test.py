from __future__ import division
from demo import *


POP = 'LNS10000000'
EMP = 'LNS12000000'
UNE = 'LNS13000000'

series = [
    'LNS10000000', # Population Level
    'LNS12000000', # Employment Level
    'LNS13000000', # Unemployment Level
]

result = bls_series(series, startyear='2015', endyear='2015')

inform = dict(zip(series, ([],[],[])))

for idx in xrange(2):
    for s in result['Results']['series']:
        inform[s['seriesID']].append(int(s['data'][idx]['value']))

    data = [inform[s][idx] for s in (POP, EMP, UNE)]
    data.append(data[1]/data[0] ** 100)
    data.append(data[2]/data[0] ** 100)

    print "%d pop, %d emp, %d unemp: %0.3f employment, %0.3f unemployment" % tuple(data)



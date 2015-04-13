# elmr.filters
# Custom filters for the template renderer, mostly extending humanize
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Apr 13 06:30:16 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: filters.py [] benjamin@bengfort.com $

"""
Custom filters for the template renderer, mostly extending humanize
"""

##########################################################################
## Imports
##########################################################################

import elmr
import humanize


##########################################################################
## Humanize Filters
##########################################################################

@elmr.app.template_filter('intcomma')
def intcomma_filter(number, cast=True):
    """
    Formats a number with `humanize.intcomma` - if cast is True, will ensure
    that all strings are converted to ints, which could raise an exception.
    """

    if isinstance(number, basestring) and cast:
        number = int(number)

    return humanize.intcomma(number)


@elmr.app.template_filter('naturaldelta')
def naturaldelta_filter(number, months=True):
    """
    Given a timedelta object or a number of seconds, converts into a human
    readable fuzzy time representation, e.g. "three seconds".
    """
    return humanize.naturaldelta(number, months)

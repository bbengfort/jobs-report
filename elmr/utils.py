# elmr.utils
# Utility functions and classes for ELMR
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Apr 09 20:29:41 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: utils.py [] benjamin@bengfort.com $

"""
Utility functions and classes for ELMR
"""

##########################################################################
## Imports
##########################################################################

import re

from datetime import datetime
from datetime import timedelta
from dateutil.tz import tzutc
from calendar import monthrange
from unicodedata import normalize

##########################################################################
## Sane Constants
##########################################################################

JSON_FMT = "%Y-%m-%dT%H:%M:%S.%f%z"

##########################################################################
## Time helpers
##########################################################################


def utcnow():
    """
    Returns timezone aware utcnow datetime
    """
    return datetime.now(tzutc())


def months_since(dt):
    """
    Computes the number of months since a datetime (compared with UTC now)

    TODO: Handle both timezone aware and unaaware datetimes
    """
    return months_between(dt, utcnow())


def months_between(dta, dtb):
    """
    Computes the number of months between two datetimes. Note that dtb must
    be bigger than dta in order for this function to work. Timezones also
    matter!
    """

    delta = 0
    while True:
        mdays = monthrange(dta.year, dta.month)[1]
        dta += timedelta(days=mdays)

        if dta <= dtb:
            delta += 1
        else:
            break

    return delta

##########################################################################
## Decorators and Descriptors
##########################################################################


class ClassPropertyDescriptor(object):

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)


def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)

##########################################################################
## URL Helpers
##########################################################################

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'-'):
    """
    Returns a URL safe slug of the given text.
    """
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))

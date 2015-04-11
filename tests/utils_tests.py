# utils_tests
# Testing the elmr.utils module
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Apr 09 20:31:20 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: utils_tests.py [] benjamin@bengfort.com $

"""
Testing the elmr.utils module
"""

##########################################################################
## Imports
##########################################################################

import unittest

from dateutil.tz import tzutc
from elmr.utils import classproperty
from datetime import datetime, timedelta
from elmr.utils import utcnow, months_since, months_between

##########################################################################
## Time Helper Tests
##########################################################################


class TimeHelperTests(unittest.TestCase):

    def test_utcnow(self):
        """
        Assert that timezone aware datetime is returned from utcnow
        """
        dt = utcnow()
        self.assertIsNotNone(dt.tzinfo)
        self.assertEqual(dt.tzname(), 'UTC')

    def test_months_between(self):
        """
        Test the months between helper
        """

        dta = datetime(2015, 4, 15, 12, 0, 0)
        dtb = dta + timedelta(days=29)
        self.assertEqual(months_between(dta, dtb), 0)

        dtb = dta + timedelta(days=30)
        self.assertEqual(months_between(dta, dtb), 1)

        dta = datetime(2015, 5, 15, 12, 0, 0)
        dtb = dta + timedelta(days=30)
        self.assertEqual(months_between(dta, dtb), 0)

        dtb = dta + timedelta(days=31)
        self.assertEqual(months_between(dta, dtb), 1)

        dta = datetime(2015, 2, 14, 12, 0, 0)
        dtb = dta + timedelta(days=27)
        self.assertEqual(months_between(dta, dtb), 0)

        dtb = dta + timedelta(days=28)
        self.assertEqual(months_between(dta, dtb), 1)

        dta = datetime(2015, 3, 15, 12, 0, 0)
        dtb = dta + timedelta(days=400)
        self.assertEqual(months_between(dta, dtb), 13)

        dta = datetime(2015, 3, 15, 12, 0, 0)
        dtb = dta + timedelta(days=1000)
        self.assertEqual(months_between(dta, dtb), 32)

    def test_months_between_tz_aware(self):
        """
        Test the months between helper with timezones
        """

        dta = datetime(2015, 4, 15, 12, 0, 0)
        dta.replace(tzinfo=tzutc())
        dtb = dta + timedelta(days=29)
        self.assertEqual(months_between(dta, dtb), 0)

        dtb = dta + timedelta(days=30)
        self.assertEqual(months_between(dta, dtb), 1)

        dtb = dta + timedelta(days=91)
        self.assertEqual(months_between(dta, dtb), 3)

    def test_months_since(self):
        """
        Test timezone aware months since
        """
        dt = utcnow() - timedelta(days=235)
        self.assertEqual(months_since(dt), 7)


##########################################################################
## Descriptor and Decorator Tests
##########################################################################


class DecoratorTests(unittest.TestCase):

    class Bar(object):

        _bar = 42

        @classproperty
        def bar(cls):
            return cls._bar

    def test_get_classproperty(self):
        """
        Check that the class property works correctly
        """

        self.assertEqual(self.Bar.bar, self.Bar._bar)

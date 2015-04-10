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

from elmr.utils import classproperty

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

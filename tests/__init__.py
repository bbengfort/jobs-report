# tests
# Tests for the Jobs Report Application
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue Mar 03 09:11:22 2015 -0500
#
# Copyright (C) 2014 University of Maryland
# For license information, see LICENSE.txt
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
Tests for the Jobs Report Application
"""

##########################################################################
## Imports
##########################################################################

import os
import unittest

##########################################################################
## Initialization Tests
##########################################################################

EXPECTED_VERSION = "0.3.4"


class InitializationTests(unittest.TestCase):

    def test_sanity(self):
        """
        Check the world is sane and 2+2=4
        """

        self.assertEqual(2 + 2, 4)

    def test_import(self):
        """
        Ensure we can import the elmr module
        """

        try:
            import elmr
        except ImportError:
            self.fail("Could not import the ELMR module")

    def test_version(self):
        """
        Check that the test version matches the ELMR version
        """

        import elmr
        self.assertEqual(elmr.__version__, EXPECTED_VERSION)

    def test_testing_mode(self):
        """
        Assert that we are in testing mode
        """
        self.assertEqual(os.environ["ELMR_SETTINGS"], "testing")

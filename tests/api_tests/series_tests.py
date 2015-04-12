# tests.api_tests.series_tests
# Test the series endpoint of the API.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Apr 12 14:01:26 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: series_tests.py [] benjamin@bengfort.com $

"""
Test the series endpoint of the API.
"""

##########################################################################
## Imports
##########################################################################

import elmr

from flask.ext.testing import TestCase
from tests.initdb import syncdb, dropdb, loaddb

##########################################################################
## Test Cases
##########################################################################


class SeriesGETTests(TestCase):
    """
    Tests the series endpoint for anything requriing loaded fixtures.
    """

    def create_app(self):
        elmr.app.config.from_object('elmr.config.TestingConfig')
        return elmr.app

    @classmethod
    def setUpClass(cls):
        syncdb()
        loaddb()

    @classmethod
    def tearDownClass(cls):
        dropdb()

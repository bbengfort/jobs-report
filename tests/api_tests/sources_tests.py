# tests.api_tests.sources_tests
# Test the sources endpoint of the API.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Apr 12 14:04:12 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: sources_tests.py [] benjamin@bengfort.com $

"""
Test the sources endpoint of the API.
"""

##########################################################################
## Imports
##########################################################################

import elmr

from flask.ext.testing import TestCase
from tests.initdb import syncdb, dropdb, loaddb
from tests import EXPECTED_VERSION
from elmr.config import TestingConfig

##########################################################################
## Test Cases
##########################################################################


class SourcesGETTests(TestCase):
    """
    Tests the sources endpoint for anything requriing loaded fixtures.
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

    def test_add_slash_sources_list(self):
        """
        Test that a slash is added to the end of the sources list.

        See test_add_sources_detail note.
        """
        response = self.client.get("/api/source")
        self.assertEquals(response.status_code, 301)
        self.assertIsNotNone(response.location)
        self.assertTrue(response.location.endswith("/"))

    def test_add_slash_sources_detail(self):
        """
        Test that a slash is added to the end of the sources detail.

        Note: if this test fails, ensure the add_resource call includes a
        trailing slash in the endpoint definition (how this is setup)
        """
        response = self.client.get("/api/source/CPS")
        self.assertEquals(response.status_code, 301)
        self.assertIsNotNone(response.location)
        self.assertTrue(response.location.endswith("/"))

    def test_get_sources_list(self):
        """
        Test that the sources list can be fetched
        """
        response = self.client.get("/api/source/")
        self.assertEquals(response.status_code, 200)

        for key in ('sources',):
            self.assertIn(key, response.json)

        self.assertEqual(len(response.json['sources']), 8)

        for s in response.json['sources']:
            for key in ('name', 'records', 'url'):
                self.assertIn(key, s)

        expected = {
            'CESN', 'CESN-ANALYSIS',
            'LAUS', 'LAUS-ANALYSIS',
            'CESSM', 'CESSM-ANALYSIS',
            'CPS', 'CPS-ANALYSIS',
        }

        returned = set([s["name"] for s in response.json['sources']])
        self.assertEqual(expected, returned)

    def test_cps_source(self):
        """
        Test that the CPS source can be fetched
        """

        response = self.client.get("/api/source/CPS/")
        self.assertEquals(response.status_code, 200)

        # Test attributes of the source
        required_keys = ('data', 'period', 'title', 'version', 'descriptions')
        for key in required_keys:
            self.assertIn(key, response.json)

        # Test the length of the data and descriptions
        self.assertEqual(len(response.json['data']), 24)
        self.assertEqual(len(response.json['descriptions']), 40)

        # Test the version and the title
        self.assertEqual(response.json['version'], EXPECTED_VERSION)
        self.assertNotEqual(response.json['title'], "")
        self.assertIsNotNone(response.json['title'])

        start = "Jan %s" % TestingConfig.STARTYEAR
        end   = "Dec %s" % TestingConfig.ENDYEAR

        period = response.json['period']
        self.assertIn('start', period)
        self.assertIn('end', period)
        self.assertEqual(period['start'], start)
        self.assertEqual(period['end'], end)

    def test_cesn_source(self):
        """
        Test that the CESN source can be fetched
        """

        response = self.client.get("/api/source/CESN/")
        self.assertEquals(response.status_code, 200)

        # Test attributes of the source
        required_keys = ('data', 'period', 'title', 'version', 'descriptions')
        for key in required_keys:
            self.assertIn(key, response.json)

        # Test the length of the data and descriptions
        self.assertEqual(len(response.json['data']), 24)
        self.assertEqual(len(response.json['descriptions']), 33)

        # Test the version and the title
        self.assertEqual(response.json['version'], EXPECTED_VERSION)
        self.assertNotEqual(response.json['title'], "")
        self.assertIsNotNone(response.json['title'])

        start = "Jan %s" % TestingConfig.STARTYEAR
        end   = "Dec %s" % TestingConfig.ENDYEAR

        period = response.json['period']
        self.assertIn('start', period)
        self.assertIn('end', period)
        self.assertEqual(period['start'], start)
        self.assertEqual(period['end'], end)

    def test_laus_source(self):
        """
        Test that the LAUS source can not be fetched
        """

        response = self.client.get("/api/source/LAUS/")
        self.assertEquals(response.status_code, 400)

        # Test the attributes of 400
        required_keys = ('message', 'success')
        for key in required_keys:
            self.assertIn(key, response.json)

        # Success should be fale
        self.assertFalse(response.json['success'])

        # Message should contain the bad LAUS source
        expected_message = "Source 'LAUS' is not allowed."
        self.assertEqual(response.json['message'], expected_message)

    def test_cessm_source(self):
        """
        Test that the CESSM source can not be fetched
        """

        response = self.client.get("/api/source/CESSM/")
        self.assertEquals(response.status_code, 400)

        # Test the attributes of 400
        required_keys = ('message', 'success')
        for key in required_keys:
            self.assertIn(key, response.json)

        # Success should be fale
        self.assertFalse(response.json['success'])

        # Message should contain the bad LAUS source
        expected_message = "Source 'CESSM' is not allowed."
        self.assertEqual(response.json['message'], expected_message)

    def test_404_message(self):
        """
        Assert in the case of an unknown source, 404 is returned
        """
        response = self.client.get("/api/source/bloopies/")
        self.assertEquals(response.status_code, 404)

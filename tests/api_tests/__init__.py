# tests.api_tests
# Integration testing the API endpoints of the ELMR app.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sun Apr 12 14:02:18 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
Integration testing the API endpoints of the ELMR app.
"""

##########################################################################
## Imports
##########################################################################

import elmr

from flask.ext.testing import TestCase

##########################################################################
## Test Cases
##########################################################################

EXPECTED_ENDPOINTS = {
    "heartbeat": "status",
    "series": "series",
    "sources": "source",
    "geography": "geo",
    "wealth of nations": "regions"
}


class APIListTests(TestCase):
    """
    Test the API list object
    """

    def create_app(self):
        elmr.app.config.from_object('elmr.config.TestingConfig')
        return elmr.app

    def get_endpoint(self, name):
        """
        Returns the computed API endpoint for a resource
        """
        return "http://localhost/api/%s/" % name

    def test_get_api_list(self):
        """
        Test that the api root returns an object
        """
        response = self.client.get("/api/")
        self.assertEquals(response.status_code, 200)

    def test_current_api_endpoint_list(self):
        """
        Test the response from the API root
        """
        response = self.client.get("/api/")
        self.assertEquals(response.status_code, 200)

        for key, val in EXPECTED_ENDPOINTS.items():
            self.assertIn(key, response.json)
            url = self.get_endpoint(val)
            self.assertEqual(response.json[key], url)

    def test_extra_api_endpoint_list(self):
        """
        Quick check for testing sanity, if anything isn't in expcted
        """
        response = self.client.get("/api/")
        self.assertEquals(response.status_code, 200)

        for key, val in response.json.items():
            self.assertIn(key, EXPECTED_ENDPOINTS)

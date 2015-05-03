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
import random

from elmr.models import Series
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
        cls.SERIES_IDS = [s.blsid for s in Series.query.all()]

    @classmethod
    def tearDownClass(cls):
        dropdb()

    def get_random_detail_endpoint(self):
        """
        Returns a random detail endpoint for probabilistic testing
        """
        s = random.choice(self.SERIES_IDS)
        return "/api/series/%s/" % s

    def test_add_slash_series_list(self):
        """
        Test that a slash is added to the end of the series list.

        Note: if this test fails, ensure the add_resource call includes a
        trailing slash in the endpoint definition (how this is setup)
        """
        response = self.client.get("/api/series")
        self.assertEquals(response.status_code, 301)
        self.assertIsNotNone(response.location)
        self.assertTrue(response.location.endswith("/"))

    def test_add_slash_series_detail(self):
        """
        Test that a slash is added to the end of the series detail.

        Note: if this test fails, ensure the add_resource call includes a
        trailing slash in the endpoint definition (how this is setup)
        """
        # Get an endpoint with the trailing slash stripped
        endpoint = self.get_random_detail_endpoint()[:-1]

        # Test the trailing slash endpiont
        response = self.client.get(endpoint)
        self.assertEquals(response.status_code, 301)
        self.assertIsNotNone(response.location)
        self.assertTrue(response.location.endswith("/"))

    def test_get_series_list(self):
        """
        Assert that a series list can be fetched.
        """
        response = self.client.get("/api/series/")
        self.assertEquals(response.status_code, 200)

    def test_paginated_series(self):
        """
        Assert that a series list is paginated.
        """
        response = self.client.get("/api/series/")
        self.assertEquals(response.status_code, 200)

        for key in ("page", "pages", "per_page", "total", "series"):
            self.assertIn(key, response.json)

        root = "http://localhost/api/series/"
        for s in response.json["series"]:
            for key in ("url", "blsid", "title", "source"):
                self.assertIn(key, s)
                self.assertTrue(s["url"].startswith(root))
                self.assertTrue(s["url"].endswith("/"))

        self.assertEqual(response.json["page"], 1)
        self.assertEqual(response.json["pages"], 85)
        self.assertEqual(response.json["per_page"], 20)
        self.assertEqual(response.json["total"], 1684)

    def test_next_page_series_list(self):
        """
        Test fetching other pages with the series.
        """
        response = self.client.get("/api/series/")
        self.assertEquals(response.status_code, 200)

        newpage = random.choice(xrange(1, response.json["pages"]))
        response = self.client.get("/api/series/?page=%i" % newpage)
        self.assertEquals(response.status_code, 200)

        badpage = response.json["pages"] + 23
        response = self.client.get("/api/series/?page=%i" % badpage)
        self.assertEquals(response.status_code, 404)

    def test_per_page_series_list(self):
        """
        Test changing the per page on a series list
        """
        response = self.client.get("/api/series/?per_page=50")
        self.assertEquals(response.status_code, 200)

        self.assertEqual(response.json["page"], 1)
        self.assertEqual(response.json["pages"], 34)
        self.assertEqual(response.json["per_page"], 50)
        self.assertEqual(response.json["total"], 1684)

    def test_get_series_detail(self):
        """
        Assert that a series detail can be fetched.
        """
        endpoint = self.get_random_detail_endpoint()
        response = self.client.get(endpoint)
        self.assertEquals(response.status_code, 200)

    def test_series_detail_response(self):
        """
        Test the response of a series detail
        """
        endpoint = self.get_random_detail_endpoint()
        response = self.client.get(endpoint)
        self.assertEquals(response.status_code, 200)

        for key in ("blsid", "source", "title", "data"):
            self.assertIn(key, response.json)

        sources = {"CPS", "CESN", "LAUS", "CESSM"}
        self.assertIn(response.json["source"], sources)
        self.assertEqual(len(response.json["data"]), 24)

    def test_series_detail_start_year(self):
        """
        Test that a series detail can be modified with a start year
        """
        endpoint = self.get_random_detail_endpoint() + "?start_year=2007"
        response = self.client.get(endpoint)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.json['data']), 12)

    def test_series_detail_end_year(self):
        """
        Test that a series detail can be modified with an end year
        """
        endpoint = self.get_random_detail_endpoint() + "?end_year=2006"
        response = self.client.get(endpoint)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.json['data']), 12)

    def test_series_detail_year_range(self):
        """
        Test that a series detail can be modified with a range
        """
        endpoint = self.get_random_detail_endpoint()
        endpoint += "?start_year=2006&end_year=2006"
        response = self.client.get(endpoint)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.json['data']), 12)

    def test_missing_series_detail(self):
        """
        Test that an unknown series identifier returns 404
        """

        self.assertNotIn("UMD100023301100", self.SERIES_IDS)

        response = self.client.get("/api/series/UMD100023301100/")
        self.assertEquals(response.status_code, 404)

    def test_series_detail_update(self):
        """
        Test that a PUT request can update the title
        """

        endpoint = self.get_random_detail_endpoint()
        response = self.client.get(endpoint)
        self.assertEquals(response.status_code, 200)

        oldtitle = response.json['title']

        response = self.client.put(endpoint, data={'title': 'foo'})
        self.assertEquals(response.status_code, 200)

        for key in ('blsid', 'source', 'title'):
            self.assertIn(key, response.json)

        response = self.client.get(endpoint)
        self.assertEquals(response.status_code, 200)
        self.assertNotEqual(oldtitle, response.json['title'])

    def test_series_detail_no_id_update(self):
        """
        Assert that a PUT request cannot update the blsid
        """

        endpoint = self.get_random_detail_endpoint()
        response = self.client.get(endpoint)
        self.assertEquals(response.status_code, 200)

        blsid    = response.json['blsid']

        response = self.client.put(endpoint, data={'title': 'foo', 'blsid': 'UMD122002202'})
        self.assertEquals(response.status_code, 200)

        response = self.client.get(endpoint)
        self.assertEquals(response.status_code, 200)
        self.assertEqual(blsid, response.json['blsid'])

    def test_series_detail_no_source_update(self):
        """
        Assert that a PUT request cannot update the source
        """

        endpoint = self.get_random_detail_endpoint()
        response = self.client.get(endpoint)
        self.assertEquals(response.status_code, 200)

        source    = response.json['source']

        response = self.client.put(endpoint, data={'title': 'foo', 'source': 'UMD'})
        self.assertEquals(response.status_code, 200)

        response = self.client.get(endpoint)
        self.assertEquals(response.status_code, 200)
        self.assertEqual(source, response.json['source'])

    def test_series_detail_update_title_required(self):
        """
        Assert that a title is required for a PUT
        """

        endpoint = self.get_random_detail_endpoint()
        response = self.client.put(endpoint, data={})
        self.assertEquals(response.status_code, 400)

        response = self.client.put(endpoint, data={"title": None})
        self.assertEquals(response.status_code, 400)

        response = self.client.put(endpoint, data={"title": ""})
        self.assertEquals(response.status_code, 400)
        

# tests.api_tests.heartbeat_tests
# Integration testing the hearbeat endpoints of the ELMR app.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri Apr 10 13:59:48 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: heartbeat_tests.py [] benjamin@bengfort.com $

"""
Integration testing the endpoints endpoints of the ELMR app.
"""

##########################################################################
## Imports
##########################################################################

import elmr

from tests.initdb import syncdb, dropdb
from elmr.models import IngestionRecord
from flask.ext.testing import TestCase
from datetime import datetime, timedelta


##########################################################################
## Test Cases
##########################################################################


class HeartbeatTests(TestCase):

    def create_app(self):
        elmr.app.config.from_object('elmr.config.TestingConfig')
        return elmr.app

    def setUp(self):
        syncdb()

    def tearDown(self):
        dropdb()

    def create_ingestion_record(self, days=1, duration=120):
        """
        Creates an ingestion record `days` days ago with a duration of the
        amount passed into the function. Used to create different ingestions.
        """
        started  = datetime.now() - timedelta(days=days)
        finished = started + timedelta(seconds=duration)

        record = IngestionRecord(
            title=u"ELMR Testing Fake Ingestion Record",
            version=elmr.get_version(),
            start_year=datetime(2000, 1, 1, 12, 0, 0).date(),
            end_year=datetime(2015, 1, 1, 12, 0, 0).date(),
            duration=duration,
            num_series=1684,
            num_added=327213,
            num_fetched=333421,
            started=started,
            finished=finished
        )

        elmr.db.session.add(record)
        elmr.db.session.commit()

    def test_heartbeat(self):
        """
        Check that the heartbeat gives a 200 response
        """

        response = self.client.get("/api/status/")
        self.assertEquals(response.status_code, 200)

    def test_add_slash_hearbeat(self):
        """
        Test that a slash is added to the end of the hearbeat endpoint

        Note: if this test fails, ensure the add_resource call includes a
        trailing slash in the endpoint definition (how this is setup)
        """
        response = self.client.get("/api/status")
        self.assertEquals(response.status_code, 301)
        self.assertIsNotNone(response.location)
        self.assertTrue(response.location.endswith("/"))

    def test_heartbeat_fields(self):
        """
        Check standard heartbeat fields
        """
        response = self.client.get("/api/status/")
        self.assertEquals(response.status_code, 200)
        data = response.json

        # Test the expected keys
        self.assertIn("status", data)
        self.assertIn("version", data)
        self.assertIn("timestamps", data)

    def test_initialized_heartbeat_fields(self):
        """
        Check initialized heartbeat fields
        """
        self.create_ingestion_record()

        response = self.client.get("/api/status/")
        self.assertEquals(response.status_code, 200)
        data = response.json

        # Test the expected keys
        self.assertIn("timestamps", data)
        self.assertIn("ingestion", data['timestamps'])
        self.assertIn("monthdelta", data['timestamps'])

    def test_heartbeat_version(self):
        """
        Test the heartbeat version is correct
        """

        response = self.client.get("/api/status/")
        self.assertEquals(response.status_code, 200)
        self.assertIn("version", response.json)
        self.assertEquals(elmr.get_version(), response.json["version"])

    def test_uninitialized_heartbeat(self):
        """
        Test that without an ingestion record, status is white
        """

        response = self.client.get("/api/status/")
        self.assertEquals(response.status_code, 200)
        self.assertIn("status", response.json)
        self.assertEquals("white", response.json["status"])

    def test_green_status(self):
        """
        Test an Ingestion record within a month
        """
        self.create_ingestion_record(29, 1832)

        response = self.client.get("/api/status/")
        self.assertEquals(response.status_code, 200)
        self.assertIn("status", response.json)
        self.assertEquals("green", response.json["status"])

    def test_yellow_status(self):
        """
        Test an Ingestion record within a month
        """

        self.create_ingestion_record(129, 1451)

        response = self.client.get("/api/status/")
        self.assertEquals(response.status_code, 200)
        self.assertIn("status", response.json)
        self.assertEquals("yellow", response.json["status"])

    def test_red_status(self):
        """
        Test an Ingestion record within a month
        """

        self.create_ingestion_record(439, 1529)

        response = self.client.get("/api/status/")
        self.assertEquals(response.status_code, 200)
        self.assertIn("status", response.json)
        self.assertEquals("red", response.json["status"])

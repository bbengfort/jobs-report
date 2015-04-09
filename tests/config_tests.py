# tests.config_tests
# Tests for the config module of ELMR
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Apr 09 11:59:27 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: config_tests.py [] benjamin@bengfort.com $

"""
Tests for the config module of ELMR
"""

##########################################################################
## Imports
##########################################################################

import os
import unittest

from elmr.config import settings
from elmr.config import get_settings_object
from elmr.config import Config, TestingConfig
from elmr.exceptions import ImproperlyConfigured

##########################################################################
## Configuration Tests
##########################################################################


class ConfigurationTests(unittest.TestCase):

    def test_config_properties(self):
        """
        Check required config properties -- maintain this method!
        """

        self.assertFalse(Config.DEBUG)
        self.assertFalse(Config.TESTING)
        self.assertTrue(hasattr(Config, "SECRET_KEY"))
        self.assertTrue(hasattr(Config, "CSRF_ENABLED"))
        self.assertEqual(Config.STARTYEAR, "2000")
        self.assertEqual(Config.ENDYEAR, "2015")
        self.assertTrue(Config.FIXTURES.endswith("fixtures"))

        self.assertTrue(TestingConfig.DEBUG)
        self.assertTrue(TestingConfig.TESTING)

    def test_get_settings_object(self):
        """
        Check that settings can be fetched from the environment
        """

        mode = get_settings_object("testing")
        self.assertEqual(mode, "elmr.config.TestingConfig")

    def test_get_settings_object_override(self):
        """
        Ensure that the environment can overwrite the config
        """
        orig = os.environ['ELMR_SETTINGS']
        os.environ['ELMR_SETTINGS'] = 'development'
        mode = get_settings_object("testing")
        self.assertEqual(mode, "elmr.config.DevelopmentConfig")
        os.environ['ELMR_SETTINGS'] = orig

    def test_bad_settings_name(self):
        """
        Check that bad settings name raises an error
        """
        orig = os.environ['ELMR_SETTINGS']
        os.environ['ELMR_SETTINGS'] = 'badname'

        with self.assertRaises(ImproperlyConfigured):
            get_settings_object("testing")

        os.environ['ELMR_SETTINGS'] = orig

    def test_environ_settings(self):
        """
        Check that a setting can be set with the environ
        """

        os.environ['ELMR_FOO'] = 'bar'
        self.assertEqual(settings('foo', 'baz'), 'bar')
        del os.environ['ELMR_FOO']

    def test_settings_default(self):
        """
        Check that a setting can be set with a default
        """

        self.assertEqual(settings('foo', 'baz'), 'baz')

    def test_required_settings(self):
        """
        Assert ImproperlyConfigured is raised on required settings
        """
        with self.assertRaises(ImproperlyConfigured):
            settings('baz', required=True)

    def test_required_settings_environ(self):
        """
        Assert ImproperlyConfigured is not raised when required found
        """
        os.environ['ELMR_BAZ'] = 'bingo'

        try:
            settings('baz', required=True)
        except ImproperlyConfigured:
            self.fail("ImproperlyConfigured raised when val is in environ!")

        del os.environ['ELMR_BAZ']

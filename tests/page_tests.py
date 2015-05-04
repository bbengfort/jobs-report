# tests.page_tests
# Tests the delivery of template driven pages
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Fri May 01 13:44:23 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: page_tests.py [] benjamin@bengfort.com $

"""
Tests the delivery of template driven pages
"""

##########################################################################
## Imports
##########################################################################

import elmr

from flask.ext.testing import TestCase
from tests.initdb import syncdb, dropdb


##########################################################################
## Template Testing
##########################################################################


class TemplateTests(TestCase):
    """
    Test the template delivery of pages in the app.
    """

    render_templates = False

    def create_app(self):
        elmr.app.config.from_object('elmr.config.TestingConfig')
        return elmr.app

    @classmethod
    def setUpClass(cls):
        syncdb(metatables=True)

    @classmethod
    def tearDownClass(cls):
        dropdb(metatables=True)

    def test_home_template(self):
        """
        Assert that the home page uses the home template.
        """
        reponse = self.client.get("/")
        self.assert_template_used('home.html')

    def test_admin_template(self):
        """
        Assert that the admin page uses the admin template.
        """
        reponse = self.client.get("/admin/")
        self.assert_template_used('admin.html')

    def test_benjamin_development_template(self):
        """
        Assert that the benjamin development page uses the benjamin template.
        """
        reponse = self.client.get("/benjamin/")
        self.assert_template_used('development/benjamin.html')

    def test_assaf_development_template(self):
        """
        Assert that the assaf development page uses the assaf template.
        """
        reponse = self.client.get("/assaf/")
        self.assert_template_used('development/assaf.html')

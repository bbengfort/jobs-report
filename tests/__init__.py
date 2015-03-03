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

import unittest

##########################################################################
## Initialization Tests
##########################################################################

class InitializationTests(unittest.TestCase):

    def test_sanity(self):
        """
        Check the world is sane and 2+2=4
        """
        self.assertEqual(2+2,4)

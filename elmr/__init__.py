# elmr
# Simple Flask Web Application to develop the Jobs Report
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Sat Apr 04 11:34:12 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: elmr.py [] benjamin@bengfort.com $

"""
Simple Flask Web Application to develop the Jobs Report

This file contains Flask-specific details. All that's required is to import
this module, and run the app.
"""

##########################################################################
## Primary Imports
##########################################################################

from flask import Flask
from flask.ext import restful
from elmr.version import get_version
from elmr.config import get_settings_object

##########################################################################
## Module Definition
##########################################################################

__version__ = get_version()

##########################################################################
## Configure Flask
##########################################################################

# Create Flask App
app = Flask(__name__)
api = restful.Api(app)

# Configure the App
app.config.from_object(get_settings_object("development"))

##########################################################################
## Import Resources
##########################################################################

# Import views: must be after app config
import elmr.views

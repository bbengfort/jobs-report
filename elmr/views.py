# views
# Routes for the ELMR web application
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Apr 09 09:13:29 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: views.py [] benjamin@bengfort.com $

"""
Routes for the ELMR web application
"""

##########################################################################
## Imports
##########################################################################

import os

from elmr import app
from flask import render_template, send_from_directory

##########################################################################
## Configure Routes
##########################################################################


@app.route("/")
def page():
    return render_template('home.html')


@app.route('/favicon.ico')
def favicon():
    dirname = os.path.join(app.root_path, 'static')
    return send_from_directory(dirname, 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')

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
import json  # TODO: remove

from elmr import get_version
from elmr import app, api, db
from elmr.models import IngestionRecord
from elmr.utils import JSON_FMT, utcnow, months_since

from flask.ext.restful import Resource
from flask import render_template, send_from_directory

from sqlalchemy import desc

##########################################################################
## Configure Application Routes
##########################################################################


@app.route("/")
def page():
    return render_template('home.html')


@app.route('/favicon.ico')
def favicon():
    dirname = os.path.join(app.root_path, 'static')
    return send_from_directory(dirname, 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')

##########################################################################
## Configure API Resources
##########################################################################


class TimeSeries(Resource):
    """
    Current implementation of time series data, simply load JSON file and
    returns it for now (so you can get it in two ways). This will be replaced
    soon.
    """

    def get(self):
        base = os.path.dirname(__file__)
        data = os.path.join(base, 'static', 'data', 'elmr.json')
        with open(data, 'r') as f:
            return json.load(f)


class Heartbeat(Resource):
    """
    Keep alive endpoint, if you get a 200 response, you know ELMR is alive!
    Also gives important status information like the version of ELMR, last
    ingestion time and so forth.
    """

    def get(self):

        context = {
            'status': "white",
            'version': get_version(),
            'timestamps': {
                'current': utcnow().strftime(JSON_FMT),
            }
        }

        latest = IngestionRecord.query.order_by(desc('finished')).first()

        if latest is not None:
            months = months_since(latest.finished)

            if months < 2:
                context["status"] = "green"
            elif months < 7:
                context["status"] = "yellow"
            else:
                context["status"] = "red"

            tsfields = context['timestamps']
            tsfields['ingestion']  = latest.finished.strftime(JSON_FMT)
            tsfields['monthdelta'] = months

        return context

##########################################################################
## Configure API Endpoints
##########################################################################

api.add_resource(TimeSeries, '/api/data/', endpoint='data')
api.add_resource(Heartbeat, '/api/status/', endpoint="status")

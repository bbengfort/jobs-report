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

from urlparse import urljoin

from elmr import app, api
from elmr import get_version
from elmr.models import IngestionRecord
from elmr.models import Series, SeriesRecord
from elmr.utils import JSON_FMT, utcnow, months_since

from flask import request
from flask.ext.restful import Resource, reqparse
from flask import render_template, send_from_directory

from sqlalchemy import desc, extract

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


class SeriesView(Resource):
    """
    API for getting the detail of a single time series object, probably won't
    be used for our project, but available so that we can quickly get info.
    """

    @property
    def parser(self):
        """
        Returns the default parser for the SeriesView
        """
        if not hasattr(self, '_parser'):
            self._parser = reqparse.RequestParser()
            self._parser.add_argument('start_year', type=int)
            self._parser.add_argument('end_year', type=int)
        return self._parser

    def get(self, blsid):
        """
        Returns the Series detail for a given blsid.
        """

        args    = self.parser.parse_args()
        series  = Series.query.filter_by(blsid=blsid).first_or_404()
        context = {
            "blsid": series.blsid,
            "source": series.source,
            "title": series.title,
            "data": [],
        }

        start   = args.get('start_year', None)
        finish  = args.get('end_year', None)

        # Start the records query
        records = SeriesRecord.query.filter_by(series_id=series.id)
        ryear   = extract('year', SeriesRecord.period)

        if start is not None:
            records = records.filter(ryear >= start)

        if finish is not None:
            records = records.filter(ryear <= finish)

        # Serialize the records
        for record in records.all():
            context['data'].append({
                "period": record.period.strftime("%b %Y"),
                "value": record.value
            })

        return context


class SeriesListView(Resource):
    """
    API for returning a list of time series objects.
    """

    @property
    def parser(self):
        """
        Returns the default parser for the SeriesView
        """
        if not hasattr(self, '_parser'):
            self._parser = reqparse.RequestParser()
            self._parser.add_argument('page', type=int)
            self._parser.add_argument('per_page', type=int)
        return self._parser

    def get(self):
        """
        Returns a list of the Series objects.
        """

        args     = self.parser.parse_args()
        page     = args.page or 1
        per_page = args.per_page or 20
        series   = Series.query.paginate(page, per_page)

        context = {
            "page": series.page,
            "pages": series.pages,
            "per_page": series.per_page,
            "total": series.total,
            "series": [],
        }

        for item in series.items:
            context["series"].append({
                "url": self.get_detail_url(item.blsid),
                "blsid": item.blsid,
                "title": item.title,
                "source": item.source,
            })

        return context

    def get_detail_url(self, blsid):
        """
        Returns the blsid from the request object.
        """
        base = request.url_root
        return urljoin(base, "/api/series/%s/" % blsid)


class HeartbeatView(Resource):
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
api.add_resource(HeartbeatView, '/api/status/', endpoint="status-detail")
api.add_resource(SeriesListView, '/api/series/', endpoint='series-list')
api.add_resource(SeriesView, '/api/series/<blsid>/', endpoint='series-detail')

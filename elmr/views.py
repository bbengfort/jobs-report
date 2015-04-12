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

from elmr import app, api
from elmr import get_version
from elmr.models import IngestionRecord
from elmr.models import Series, SeriesRecord
from elmr.utils import JSON_FMT, utcnow, months_since

from flask import request
from flask.ext.restful import Resource, reqparse
from flask import render_template, send_from_directory

from urlparse import urljoin
from operator import itemgetter
from collections import defaultdict
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


class SeriesSourceView(Resource):
    """
    Another list view which returns all of the timeseries for a given source.

    At the moment, only two sources are accepted: CESN (CES - National) and
    CPS. LAUS and CESSM (CES - State and Metro) are state based APIs and
    cannot be returned in aggregate as the national sources can.

    TODO: Move allowed sources to the database.
    """

    ALLOWED_SOURCES   = set(["CESN", "CPS"])
    FORBIDDEN_SOURCES = set(["LAUS", "CESSM"])

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

    def get(self, source):
        """
        For a single source, return a data detail view for all time series.
        """

        # Ensure that source is allowed
        source = source.upper()
        if source in self.FORBIDDEN_SOURCES:
            context = {
                'success': False,
                'message': "Source '%s' is not allowed." % source,
            }
            return context, 400

        if source not in self.ALLOWED_SOURCES:
            context = {
                'success': False,
                'message': "Source '%s' is not found." % source,
            }
            return context, 404

        args    = self.parser.parse_args()
        series  = Series.query.filter_by(source=source)

        start   = args.start_year or int(app.config['STARTYEAR'])
        finish  = args.end_year or int(app.config['ENDYEAR'])

        context = {
            "title": "ELMR Ingested %s Data" % source,
            "version": get_version(),
            "period": {
                "start": start,
                "end": finish,
            },
            "descriptions": {},
            "data": [],
        }

        data = defaultdict(dict)
        for s in series.all():
            context["descriptions"][s.blsid] = s.title

            records = SeriesRecord.query.filter_by(series_id=s.id)
            ryear   = extract('year', SeriesRecord.period)
            records = records.filter(ryear >= start)
            records = records.filter(ryear <= finish)

            for record in records.all():
                data[record.period][s.blsid] = record.value

        data = sorted(data.items(), key=itemgetter(0))
        for (date, values) in data:
            values["YEAR"]  = date.year
            values["MONTH"] = date.month
            values["DATE"]  = date.strftime("%b %Y")

            context["data"].append(values)

        context['period']['start'] = data[0][0].strftime("%b %Y")
        context['period']['end']   = data[-1][0].strftime("%b %Y")

        return context

##########################################################################
## Heartbeat resource
##########################################################################


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

api.add_resource(SeriesSourceView, '/api/source/<source>/', endpoint='source')
api.add_resource(HeartbeatView, '/api/status/', endpoint="status-detail")
api.add_resource(SeriesListView, '/api/series/', endpoint='series-list')
api.add_resource(SeriesView, '/api/series/<blsid>/', endpoint='series-detail')

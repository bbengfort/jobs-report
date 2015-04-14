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

from elmr import app, api,db
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
def index():
    return render_template('home.html')


@app.route("/admin/")
def admin():
    ingestions = IngestionRecord.query.order_by(desc("id")).limit(20)
    dbcounts   = {
        "series": Series.query.count(),
        "records": SeriesRecord.query.count(),
        "ingests": IngestionRecord.query.count(),
    }
    return render_template('admin.html', ingestlog=ingestions,
                           dbcounts=dbcounts)


@app.route('/favicon.ico')
def favicon():
    dirname = os.path.join(app.root_path, 'static')
    return send_from_directory(dirname, 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')

##########################################################################
## Configure Series-Related API Resources
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


class SourceView(Resource):
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


class SourceListView(Resource):
    """
    API Resource for returning a list of sources.
    """

    def get(self):
        context = {
            "sources": []
        }

        # Create sources model in the future
        sql = "SELECT source, count(id) FROM series GROUP BY source"
        for s in db.session.execute(sql):
            context["sources"].append({
                "url": self.get_detail_url(s[0]),
                "name": s[0],
                "records": s[1],
            })

        return context

    def get_detail_url(self, name):
        """
        Returns the blsid from the request object.
        """
        base = request.url_root
        return urljoin(base, "/api/source/%s/" % name)


##########################################################################
## Configure Geography-Related API Resources
##########################################################################

import csv
import StringIO
from flask import make_response
from datetime import date, timedelta


@app.route('/api/geo/<source>/')
def geography_csv(source):
    series = [
        ('LASST010000000000006', 'Alabama', 'US01'),
        ('LASST020000000000006', 'Alaska', 'US02'),
        ('LASST040000000000006', 'Arizona', 'US04'),
        ('LASST050000000000006', 'Arkansas', 'US05'),
        ('LASST060000000000006', 'California', 'US06'),
        ('LASST080000000000006', 'Colorado', 'US08'),
        ('LASST090000000000006', 'Connecticut', 'US09'),
        ('LASST100000000000006', 'Delaware', 'US10'),
        ('LASST120000000000006', 'Florida', 'US12'),
        ('LASST130000000000006', 'Georgia', 'US13'),
        ('LASST150000000000006', 'Hawaii', 'US15'),
        ('LASST160000000000006', 'Idaho', 'US16'),
        ('LASST170000000000006', 'Illinois', 'US17'),
        ('LASST180000000000006', 'Indiana', 'US18'),
        ('LASST190000000000006', 'Iowa', 'US19'),
        ('LASST200000000000006', 'Kansas', 'US20'),
        ('LASST210000000000006', 'Kentucky', 'US21'),
        ('LASST220000000000006', 'Louisiana', 'US22'),
        ('LASST230000000000006', 'Maine', 'US23'),
        ('LASST240000000000006', 'Maryland', 'US24'),
        ('LASST250000000000006', 'Massachusetts', 'US25'),
        ('LASST260000000000006', 'Michigan', 'US26'),
        ('LASST270000000000006', 'Minnesota', 'US27'),
        ('LASST280000000000006', 'Mississippi', 'US28'),
        ('LASST290000000000006', 'Missouri', 'US29'),
        ('LASST300000000000006', 'Montana', 'US30'),
        ('LASST310000000000006', 'Nebraska', 'US31'),
        ('LASST320000000000006', 'Nevada', 'US32'),
        ('LASST330000000000006', 'New Hampshire', 'US33'),
        ('LASST340000000000006', 'New Jersey', 'US34'),
        ('LASST350000000000006', 'New Mexico', 'US35'),
        ('LASST360000000000006', 'New York', 'US36'),
        ('LASST370000000000006', 'North Carolina', 'US37'),
        ('LASST380000000000006', 'North Dakota', 'US38'),
        ('LASST390000000000006', 'Ohio', 'US39'),
        ('LASST400000000000006', 'Oklahoma', 'US40'),
        ('LASST410000000000006', 'Oregon', 'US41'),
        ('LASST420000000000006', 'Pennsylvania', 'US42'),
        ('LASST440000000000006', 'Rhode Island', 'US44'),
        ('LASST450000000000006', 'South Carolina', 'US45'),
        ('LASST460000000000006', 'South Dakota', 'US46'),
        ('LASST470000000000006', 'Tennessee', 'US47'),
        ('LASST480000000000006', 'Texas', 'US48'),
        ('LASST490000000000006', 'Utah', 'US49'),
        ('LASST500000000000006', 'Vermont', 'US50'),
        ('LASST510000000000006', 'Virginia', 'US51'),
        ('LASST530000000000006', 'Washington', 'US53'),
        ('LASST540000000000006', 'West Virginia', 'US54'),
        ('LASST550000000000006', 'Wisconsin', 'US55'),
        ('LASST560000000000006', 'Wyoming', 'US56'),
    ]

    f = StringIO.StringIO()
    fields = ["fips", "State"]

    for year in xrange(2000, 2016):
        for month in xrange(1, 13):
            if year == 2015 and month > 2:
                continue
            fields.append(date(year, month, 1).strftime("%b %Y"))

    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    for sid, state, fips in series:
        series = Series.query.filter_by(blsid=sid).first()
        row = {
            "fips": fips,
            "State": state,
        }

        for record in series.records:
            row[record.period.strftime("%b %Y")] = record.value

        writer.writerow(row)

    output = make_response(f.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=unemployment.csv"
    output.headers["Content-Type"] = "text/csv"
    return output

# class GeographyView(Resource):
#     """
#     This endpoint makes geography related data sets available - e.g. all series
#     data for individual states or full data sets for all states to power the
#     geographic visualizations on the main page.
#     """
#
#     def get(self, source):
#         """
#         Temporary geography endpoint for testing.
#
#         Right now this only returns a CSV for the employment data.
#         """
#
#         start  = "Jan 2000"
#         finish = "Mar 2015"
#
#         context = {
#             "title": "ELMR %s Geographic Data" % source,
#             "version": get_version(),
#             "period": {
#                 "start": start,
#                 "end": finish,
#             },
#             "descriptions": {},
#             "data": [],
#         }
#
#         return context

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
## API Endpoints resource
##########################################################################


class APIListView(Resource):
    """
    Returns a list of API endpoints and their names. Currently hardcoded,
    so this needs to be modified every time you add a resource to the API.
    """

    RESOURCES = {
        "heartbeat": "status",
        "sources": "source",
        "series": "series",
        "geography": "geo",
    }

    def get(self):
        """
        Returns an object describing the API.
        """

        return dict([(k, self.get_detail_url(v))
                    for (k, v) in self.RESOURCES.items()])

    def get_detail_url(self, name):
        """
        Returns the blsid from the request object.
        """
        base = request.url_root
        return urljoin(base, "/api/%s/" % name)

##########################################################################
## Configure API Endpoints
##########################################################################

# reduce the amount of typing
endpoint = api.add_resource

# configure api urls
endpoint(APIListView, '/api/')
endpoint(SourceListView, '/api/source/', endpoint='source-list')
endpoint(SourceView, '/api/source/<source>/', endpoint='source-detail')
endpoint(HeartbeatView, '/api/status/', endpoint="status-detail")
endpoint(SeriesListView, '/api/series/', endpoint='series-list')
endpoint(SeriesView, '/api/series/<blsid>/', endpoint='series-detail')
# endpoint(GeographyView, '/api/geo/<source>/', endpoint='geography-detail')

# Did you forget to modify the API list view?

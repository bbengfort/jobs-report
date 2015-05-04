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
import StringIO

from elmr import get_version
from elmr import app, api, db
from elmr.models import IngestionRecord
from elmr.models import Series, SeriesRecord, StateSeries
from elmr.utils import JSON_FMT, utcnow, months_since, slugify
from elmr.fips import write_states_dataset

from flask import request, make_response
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
    sources = (
        ("CPS", Series.query.filter_by(source="CPS")),
        ("CESN", Series.query.filter_by(source="CESN")),
        ("LAUS", Series.query.filter_by(source="LAUS")),
        ("CESSM", Series.query.filter_by(source="CESSM")),
    )
    return render_template('home.html', sources=sources)


@app.route("/admin/")
def admin():
    ingestions = IngestionRecord.query.order_by(desc("id")).limit(20)
    dbcounts   = {
        "series": Series.query.count(),
        "records": SeriesRecord.query.count(),
        "ingests": IngestionRecord.query.count(),
        "states_series": StateSeries.query.count(),
    }
    dbversion  = list(db.session.execute("SELECT * FROM migrate_version"))[0]
    return render_template('admin.html', ingestlog=ingestions,
                           dbcounts=dbcounts, dbversion=dbversion)


@app.route('/favicon.ico')
def favicon():
    dirname = os.path.join(app.root_path, 'static')
    return send_from_directory(dirname, 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


## Development Pages

@app.route('/assaf/')
def assaf_dev():
    """
    Assaf - add any context you need for your page here.
    """
    return render_template('development/assaf.html')


@app.route('/benjamin/')
def benjamin_dev():
    """
    Used for Ben's independent development
    """
    return render_template('development/benjamin.html')

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

    @property
    def detail_parser(self):
        """
        Returns the detail parser for the SeriesView (for PUT)
        """
        if not hasattr(self, '_detail_parser'):
            self._detail_parser = reqparse.RequestParser()
            self._detail_parser.add_argument('title', type=str, required=True)
        return self._detail_parser

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

    def put(self, blsid):
        """
        Allows you to update the title of a BLS series
        """
        series = Series.query.filter_by(blsid=blsid).first_or_404()
        args   = self.detail_parser.parse_args()

        if not args.get('title', None):
            return {"message": "[title]: cannot be an empty string or None"}, 400

        series.title = args['title']
        db.session.commit()

        return {
            'blsid': series.blsid,
            'source': series.source,
            'title': series.title,
        }


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
            self._parser.add_argument('source', type=str)
        return self._parser

    def get(self):
        """
        Returns a list of the Series objects.
        """

        args     = self.parser.parse_args()
        page     = args.page or 1
        per_page = args.per_page or 20
        source   = args.source

        if source is not None:
            series = Series.query.filter_by(source=source)
            series = series.paginate(page, per_page)
        else:
            series = Series.query.paginate(page, per_page)

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

ALLOWED_GEO_SOURCES   = set(["LAUS", "CESSM"])
FORBIDDEN_GEO_SOURCES = set(["CESN", "CPS"])


class GeoSourcesView(Resource):
    """
    Returns the availabe sources for geography based API lookups.
    """

    def get(self):
        """
        Returns all the distinct sources and their urls
        """

        context = {
            "title": "Geographic BLS Sources",
            "sources": [],
        }

        query = "SELECT DISTINCT source FROM states_series"
        for row in db.session.execute(query):
            context["sources"].append({
                "name": row[0],
                "url": self.get_detail_url(row[0]),
            })

        return context

    def get_detail_url(self, source):
        """
        Returns the blsid from the request object.
        """
        base = request.url_root
        return urljoin(base, "/api/geo/%s/" % source)


class GeoDatasetsView(Resource):
    """
    Returns the available datasets for a geo resource.
    """

    def get(self, source):
        """
        For a given source, returns the available datasets and their counts.
        """
        # Ensure that source is allowed
        source = source.upper()
        if source in FORBIDDEN_GEO_SOURCES:
            context = {
                'success': False,
                'message': "Source '%s' is not allowed." % source,
            }
            return context, 400

        if source not in ALLOWED_GEO_SOURCES:
            context = {
                'success': False,
                'message': "Source '%s' is not found." % source,
            }
            return context, 404

        query = "SELECT distinct %s FROM states_series WHERE source='%s'"
        field = {
            "LAUS": "dataset",
            "CESSM": "category",
        }[source]

        query   = query % (field, source)
        context = {
            "title": "ELMR %s Datasets" % source,
            "field": field,
            "datasets": []
        }

        for row in db.session.execute(query):
            context["datasets"].append({
                "name": row[0],
                "url": self.get_detail_url(source, row[0]),
            })

        return context

    def get_detail_url(self, source, dataset):
        """
        Returns the blsid from the request object.
        """
        base = request.url_root
        return urljoin(base, "/api/geo/%s/%s/" % (source, slugify(dataset)))


@app.route('/api/geo/<source>/<dataset>/')
def geography_csv(source, dataset):
    """
    Returns a CSV data set for the specified source and dataset. Note that this
    must be a Flask route function and not a RESTful class because the returned
    datatype is CSV and not JSON.
    """

    source  = source.upper()

    if source in FORBIDDEN_GEO_SOURCES:
        return make_response("Source '%s' is not geographic." % source), 400

    if source not in ALLOWED_GEO_SOURCES:
        return make_response("Unknown data source -- '%s'" % source), 404

    # Determine the series from the source and the dataset

    # Create a file-like object for the CSV to return, then write the series
    csv = StringIO.StringIO()
    write_states_dataset(csv, source, dataset)

    output = make_response(csv.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=%s.csv" % dataset
    output.headers["Content-Type"] = "text/csv"
    return output

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
endpoint(GeoSourcesView, '/api/geo/', endpoint='geography-list')
endpoint(GeoDatasetsView, '/api/geo/<source>/', endpoint='geography-datasets')

# Did you forget to modify the API list view?

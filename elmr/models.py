# elmr.models
# Database models for the ELMR application
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Apr 09 14:34:57 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: models.py [] benjamin@bengfort.com $

"""
Database models for the ELMR application
"""

##########################################################################
## Imports
##########################################################################

from elmr import db
from datetime import datetime

##########################################################################
## Ingestion Models
##########################################################################


class IngestionRecord(db.Model):
    """
    Stores information about when data was ingested from the BLS API.
    """

    __tablename__ = "ingestions"

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.Unicode(255), nullable=True)
    version     = db.Column(db.Unicode(10), nullable=False)
    start_year  = db.Column(db.Date, nullable=False)
    end_year    = db.Column(db.Date, nullable=False)
    duration    = db.Column(db.Float, nullable=False)
    num_series  = db.Column(db.Integer, default=0)
    num_added   = db.Column(db.Integer, default=0)
    num_fetched = db.Column(db.Integer, default=0)
    started     = db.Column(db.DateTime(timezone=True), nullable=False,
                            default=datetime.now)
    finished    = db.Column(db.DateTime(timezone=True), nullable=False,
                            default=datetime.now, onupdate=datetime.now)

##########################################################################
## Time Series Information
##########################################################################


class Series(db.Model):
    """
    Stores information about TimeSeries data on the BLS API
    """

    __tablename__ = "series"

    id          = db.Column(db.Integer, primary_key=True)
    blsid       = db.Column(db.Unicode(255), unique=True, index=True)
    title       = db.Column(db.Unicode(255), nullable=True)
    source      = db.Column(db.Unicode(255), nullable=True)
    is_primary  = db.Column(db.Boolean, default=False)
    records     = db.relationship('SeriesRecord', backref='series',
                                  lazy='dynamic')


class SeriesRecord(db.Model):
    """
    Stores individual data points for each time series.
    """

    __tablename__ = "records"

    id          = db.Column(db.Integer, primary_key=True)
    series_id   = db.Column(db.Integer, db.ForeignKey('series.id'))
    period      = db.Column(db.Date, nullable=False, index=True)
    value       = db.Column(db.Float, nullable=False)
    footnote    = db.Column(db.Unicode(255), nullable=True)

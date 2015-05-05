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

    def __repr__(self):
        ts = self.finished.strftime("%Y-%m-%d")
        return ("<Ingestion on %s with %i records added from %i series>"
                % (ts, self.num_added, self.num_series))

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
    states      = db.relationship('StateSeries', backref='series',
                                  lazy='dynamic')

    def __repr__(self):
        return "<Series %s>" % self.blsid


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

    def __repr__(self):
        my = self.period.strftime("%B %Y")
        return ("<Record for %s - %0.2f on %s>" %
                (self.series.blsid, self.value, my))

##########################################################################
## Per-State Information
##########################################################################


class USAState(db.Model):
    """
    Stores information related to States of the United States for quickly
    extracting information from the LAUS and CESSM data sets.

    This model is based on the Federal Information Processing Standard (FIPS):
    http://en.wikipedia.org/wiki/Federal_Information_Processing_Standard_state_code

    And the FIPS codes are used in the front-end to identify states.

    Note that series returns the state series mapping table, not series objects
    itself without another lookup.

    The region is the Bureau of Economic Analysis regions:
    http://en.wikipedia.org/wiki/List_of_regions_of_the_United_States#Bureau_of_Economic_Analysis_regions
    """

    __tablename__ = "usa_states"

    id          = db.Column(db.Integer, primary_key=True)
    fips        = db.Column(db.Unicode(5), unique=True, index=True)
    name        = db.Column(db.Unicode(255), nullable=False)
    abbr        = db.Column(db.Unicode(2), nullable=True)
    region      = db.Column(db.Unicode(15), nullable=True)
    series      = db.relationship('StateSeries', backref='state',
                                  lazy='dynamic')

    def __repr__(self):
        return "<%s (%s)>" % (self.name, self.fips)


class StateSeries(db.Model):
    """
    Many-to-Many mapping of states to series (even though in reality it is a
    one to many relationship, this table allows us to store extra data). Use
    this table to quickly fetch all of the series related to a particular
    state or to fetch state data for a series.

    Adjusted: Refers to seasonally adjsuted
    Dataset:  "unemployment rate", "unemployment", "employment", "labor force"
    Source:   LAUS, CESSM
    Category: For CESSM only, refers to the labor category
    Slug:     Group identifier from a URL (slugified dataset for LAUS, Category for CESSM)
    """

    __tablename__ = "states_series"

    id          = db.Column(db.Integer, primary_key=True)
    state_id    = db.Column(db.Integer, db.ForeignKey('usa_states.id'))
    series_id   = db.Column(db.Integer, db.ForeignKey('series.id'))
    adjusted    = db.Column(db.Boolean, default=False)
    dataset     = db.Column(db.Unicode(255), nullable=False)
    source      = db.Column(db.Unicode(255), nullable=True)
    category    = db.Column(db.Unicode(255), nullable=True)
    slug        = db.Column(db.Unicode(255))

    def __repr__(self):
        return "<%s %s>" % (self.state.name, self.series.blsid)

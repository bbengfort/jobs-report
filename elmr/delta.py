# elmr.delta
# Compute rates of changes in time series
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue May 05 02:32:22 2015 -0400
#
# Copyright (C) 2015 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: delta.py [] benjamin@bengfort.com $

"""
Compute rates of changes in time series by creating new timeseries that are
linked to the old time series, which expresses the delta. Precomputation
creates more data in the database, but makes faster computation.
"""

##########################################################################
## Imports
##########################################################################

from elmr.models import Series

##########################################################################
## Functions
##########################################################################


def compute_delta(series, delete=True):
    """
    For a single series computes the delta series. If the delta series exists
    the function attempts to update it. If `delete` is True, then the
    function starts over from scratch and deletes the original series. If no
    delta series exists, this function creates it.
    """

    if series.delta is None:
        # The delta series hasn't been created yet
        pass

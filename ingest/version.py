# ingest.version
# Helper module for the version of the ingestion
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Apr 06 15:23:43 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: ingest.version.py [] benjamin@bengfort.com $

"""
Helper module for the version of the ingestion
"""

##########################################################################
## Version Stuff
##########################################################################

__version__ = (1, 0, 0)


def get_version():
    """
    Reports the version
    """
    return ".".join([str(i) for i in __version__])

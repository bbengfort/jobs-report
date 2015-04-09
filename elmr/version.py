# elmr.version
# Helper module for ELMR version information
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Mon Apr 06 15:23:43 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: ingest.version.py [] benjamin@bengfort.com $

"""
Helper module for ELMR version information
"""

##########################################################################
## Versioning
##########################################################################

__version_info__ = {
    'major': 0,
    'minor': 3,
    'micro': 1,
    'releaselevel': 'final',
    'serial': 0,
}


def get_version(short=False):
    """
    Returns the version from the version info.
    """
    assert __version_info__['releaselevel'] in ('alpha', 'beta', 'final')
    vers = ["%(major)i.%(minor)i" % __version_info__, ]
    if __version_info__['micro']:
        vers.append(".%(micro)i" % __version_info__)
    if __version_info__['releaselevel'] != 'final' and not short:
        vers.append('%s%i' % (__version_info__['releaselevel'][0],
                              __version_info__['serial']))
    return ''.join(vers)

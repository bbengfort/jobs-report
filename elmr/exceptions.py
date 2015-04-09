# elmr.exceptions
# Exception hierarchy for errors and logging in ELMR
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Thu Apr 09 09:08:50 2015 -0400
#
# Copyright (C) 2015 University of Maryland
# For license information, see LICENSE.txt
#
# ID: exceptions.py [] benjamin@bengfort.com $

"""
Exception hierarchy for errors and logging in ELMR
"""

##########################################################################
## Class Hierarchy
##########################################################################


class ELMRException(Exception):
    """
    Base class for problems, logging in ELMR
    """
    pass


class ImproperlyConfigured(ELMRException):
    """
    Exception for bad configuration value.
    """
    pass

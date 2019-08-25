from __future__ import absolute_import
import datetime


def get_next_day(date):
    """ Given a date, return the next day by consulting
    the python date module """
    next_day = date + datetime.timedelta(days=1)
    return next_day

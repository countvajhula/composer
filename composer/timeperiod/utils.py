from datetime import timedelta


def get_next_day(date):
    """Given a date, return the next day by consulting
    the python date module

    :param :class:`datetime.date` date: The date to increment
    :returns :class:`datetime.date`: The next date
    """
    next_day = date + timedelta(days=1)
    return next_day


def get_next_month(date):
    """Given a date, return the start of the next month by consulting
    the python date module

    :param :class:`datetime.date` date: The date to increment
    :returns :class:`datetime.date`: The start of the next month
    """
    original_month = date.month
    while date.month == original_month:
        date = date + timedelta(days=1)
    return date

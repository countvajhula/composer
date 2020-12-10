import calendar
from datetime import date

from .base import Zero, Eternity  # noqa
from .day import Day
from .week import Week
from .month import Month
from .quarter import Quarter
from .year import Year
from .utils import get_next_day

TIME_PERIODS = (Zero, Day, Week, Month, Quarter, Year, Eternity)


def get_next_period(current_period, decreasing=False):
    """Return the next time period in sequence among the tracked
    time periods. The time periods are ordered in terms of magnitude.

    :param :class:`~composer.timeperiod.Period` current_period: A time period
    :param bool decreasing: Whether to return the next one in decreasing order
         of magnitude or increasing order (the default)
    :returns :class:`~composer.timeperiod.Period`: The next time period
    """
    periods = TIME_PERIODS
    if decreasing:
        periods = tuple(reversed(TIME_PERIODS))
    try:
        index = periods.index(current_period)
        next_period = periods[index + 1]
    except (IndexError, ValueError):
        raise
    return next_period


def get_time_periods(starting_from=None, decreasing=False):
    """Return a list of all tracked time periods.

    :param bool decreasing: Whether to return the periods in decreasing order
         of magnitude or increasing order (the default)
    :returns list: The list of time periods
    """
    periods = TIME_PERIODS
    if decreasing:
        periods = tuple(reversed(TIME_PERIODS))
    if starting_from:
        periods = periods[periods.index(starting_from) :]
    return periods


def is_weekend(date):
    """Check whether the date falls on a weekend.

    :param :class:`datetime.date` date: The date to check
    """
    dow = date.strftime('%A')
    if dow.lower() in ('saturday', 'sunday'):
        return True
    else:
        return False


def quarter_for_month(month):
    """Given a month, return the quarter that it's part of.

    :param int month: The month
    :returns str: The corresponding quarter
    """
    if month in range(1, 4):
        return "Q1"
    elif month in range(4, 7):
        return "Q2"
    elif month in range(7, 10):
        return "Q3"
    elif month in range(10, 13):
        return "Q4"


def month_for_quarter(quarter):
    """Given a quarter, return the first month of that quarter.

    :param str quarter: The quarter
    :returns int: The first month of the quarter
    """
    if quarter == "Q1":
        return 1
    elif quarter == "Q2":
        return 4
    elif quarter == "Q3":
        return 7
    elif quarter == "Q4":
        return 10


def get_month_number(monthname):
    """Get the calendar number corresponding to the month of the year.

    :param str monthname: The name of the month
    :returns int: The number of the month
    """
    month_name_to_number = dict(
        (v.lower(), k) for k, v in enumerate(calendar.month_name)
    )
    return month_name_to_number[monthname.lower()]


def get_month_name(monthnumber):
    """Get the name of the month corresponding to a calendar month number.

    :param int monthnumber: The number of the month
    :returns str: The name of the month
    """
    month_number_to_name = dict(
        (k, v) for k, v in enumerate(calendar.month_name)
    )
    return month_number_to_name[monthnumber]


def day_of_week(date):
    """Day of week for the given date.

    :param :class:`datetime.date` date: The date to check
    """
    return date.strftime("%A")


def upcoming_dow_to_date(dow, reference_date=None):
    """Date for the given upcoming day of the week.

    :param str dow: The day of the week
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    """
    if not reference_date:
        reference_date = date.today()
    d = get_next_day(reference_date)
    while day_of_week(d).lower() != dow:
        d = get_next_day(d)
    return d

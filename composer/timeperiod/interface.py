from .base import Zero  # noqa
from .day import Day
from .week import Week
from .month import Month
from .quarter import Quarter
from .year import Year

TIME_PERIODS = (Zero, Day, Week, Month, Quarter, Year)


def get_next_period(current_period, decreasing=False):
    """ Return the next time period in sequence among the tracked
    time periods. The time periods are ordered in terms of magnitude.

    :param :class:`~composer.timeperiod.Period` current_period: A time period
    :param bool decreasing: Whether to return the next one in decreasing order
         or magnitude or increasing order (the default)
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


def is_weekend(date):
    """ Check whether the date falls on a weekend.
    """
    dow = date.strftime('%A')
    if dow.lower() in ('saturday', 'sunday'):
        return True
    else:
        return False

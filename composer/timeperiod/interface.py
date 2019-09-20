from .base import Zero  # noqa
from .day import Day
from .week import Week
from .month import Month
from .quarter import Quarter
from .year import Year

TIME_PERIODS = (Zero, Day, Week, Month, Quarter, Year)


def get_next_period(current_period, decreasing=False):
    periods = TIME_PERIODS
    if decreasing:
        periods = tuple(reversed(TIME_PERIODS))
    try:
        index = periods.index(current_period)
        next_period = periods[index + 1]
    except (IndexError, ValueError):
        raise
    return next_period

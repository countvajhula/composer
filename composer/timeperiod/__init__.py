from .base import Period, Zero  # noqa
from .day import Day
from .week import Week
from .month import Month
from .quarter import Quarter
from .utils import get_next_day
from .year import Year


# TODO: move this to a module
def get_next_period(current_period, decreasing=False):
    periods = (Zero, Day, Week, Month, Quarter, Year)
    if decreasing:
        periods = tuple(reversed(periods))
    try:
        index = periods.index(current_period)
        next_period = periods[index + 1]
    except (IndexError, ValueError):
        raise
    return next_period


__all__ = (
    "get_next_day",
    "get_next_period",
    "Period",
    "Zero",
    "Day",
    "Week",
    "Month",
    "Quarter",
    "Year",
)

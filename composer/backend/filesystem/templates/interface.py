from ....timeperiod import Day, Week, Month, Quarter, Year
from .base import ZeroTemplate
from .day import DayTemplate
from .week import WeekTemplate
from .month import MonthTemplate
from .quarter import QuarterTemplate
from .year import YearTemplate


def get_template(planner, period, next_day):
    """ Get a template for the given period to mediate log file creation and
    modification.

    :param :class:`~composer.backend.filesystem.base.FilesystemPlanner`
        planner: The planner instance in connection with which log files
        are to be populated.
    :param :class:`~composer.timeperiod.Period` period: A time period
    :param :class:`datetime.date` next_day: The day we are advancing to
    :returns :class:`~composer.backend.filesystem.templates.Template`: A
        template instance
    """
    if period == Day:
        template = DayTemplate(planner, next_day)
    elif period == Week:
        template = WeekTemplate(planner, next_day)
    elif period == Month:
        template = MonthTemplate(planner, next_day)
    elif period == Quarter:
        template = QuarterTemplate(planner, next_day)
    elif period == Year:
        template = YearTemplate(planner, next_day)
    else:
        template = ZeroTemplate(planner, next_day)
    return template

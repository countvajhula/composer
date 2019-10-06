from ....timeperiod import Day, Week, Month, Quarter, Year
from .base import ZeroTemplate
from .day import DayTemplate
from .week import WeekTemplate
from .month import MonthTemplate
from .quarter import QuarterTemplate
from .year import YearTemplate


def get_template(planner, period, for_date):
    """ Get a template for the given period to mediate log file creation and
    modification.

    :param :class:`~composer.backend.filesystem.base.FilesystemPlanner`
        planner: The planner instance in connection with which log files
        are to be populated.
    :param :class:`~composer.timeperiod.Period` period: A time period
    :param :class:`datetime.date` for_date: The date for which we are getting a
        log
    :returns :class:`~composer.backend.filesystem.templates.Template`: A
        template instance
    """
    if period == Day:
        template = DayTemplate(planner, for_date)
    elif period == Week:
        template = WeekTemplate(planner, for_date)
    elif period == Month:
        template = MonthTemplate(planner, for_date)
    elif period == Quarter:
        template = QuarterTemplate(planner, for_date)
    elif period == Year:
        template = YearTemplate(planner, for_date)
    else:
        template = ZeroTemplate(planner, for_date)
    return template

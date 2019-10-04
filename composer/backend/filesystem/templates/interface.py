from ....timeperiod import Day, Week, Month, Quarter, Year
from .base import ZeroTemplate
from .day import DayTemplate
from .week import WeekTemplate
from .month import MonthTemplate
from .quarter import QuarterTemplate
from .year import YearTemplate


def get_template(planner, period, start_date):
    """ Get a template for the given period to mediate log file creation and
    modification.

    :param :class:`~composer.backend.filesystem.base.FilesystemPlanner`
        planner: The planner instance in connection with which log files
        are to be populated.
    :param :class:`~composer.timeperiod.Period` period: A time period
    :param :class:`datetime.date` start_date: The start date for the period
        for which we are getting a log
    :returns :class:`~composer.backend.filesystem.templates.Template`: A
        template instance
    """
    if period == Day:
        template = DayTemplate(planner, start_date)
    elif period == Week:
        template = WeekTemplate(planner, start_date)
    elif period == Month:
        template = MonthTemplate(planner, start_date)
    elif period == Quarter:
        template = QuarterTemplate(planner, start_date)
    elif period == Year:
        template = YearTemplate(planner, start_date)
    else:
        template = ZeroTemplate(planner, start_date)
    return template

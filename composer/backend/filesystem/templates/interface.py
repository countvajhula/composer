from ....timeperiod import Day, Week, Month, Quarter, Year
from .base import ZeroTemplate
from .day import DayTemplate
from .week import WeekTemplate
from .month import MonthTemplate
from .quarter import QuarterTemplate
from .year import YearTemplate


def get_template(planner, period, next_day):
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

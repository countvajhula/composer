from ....time import Day, Week, Month, Quarter, Year
from .day import DayTemplate
from .week import WeekTemplate
from .month import MonthTemplate
from .quarter import QuarterTemplate
from .year import YearTemplate


def _get_template(planner, period, next_day):
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
    return template


def write_new_template(planner, period, next_day):
    template = _get_template(planner, period, next_day)
    template.write_new()


def write_existing_template(planner, period, next_day):
    template = _get_template(planner, period, next_day)
    template.write_existing()

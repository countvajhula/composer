from __future__ import absolute_import
from .base import Period, PeriodAdvanceCriteria
from .day import Day

from .utils import get_next_day


class _Month(Period):

    duration = 4 * 7 * 24 * 60 * 60

    def advance_criteria_met(self, planner, now):
        next_day = get_next_day(planner.date)
        day_criteria_met = Day.advance_criteria_met(planner, now)
        if day_criteria_met == PeriodAdvanceCriteria.PlannerInFuture:
            return PeriodAdvanceCriteria.PlannerInFuture
        elif (
            next_day.day == 1
            and day_criteria_met == PeriodAdvanceCriteria.Satisfied
        ):
            return PeriodAdvanceCriteria.Satisfied

    def get_logfile(self, planner):
        return planner.monthfile

    def get_name(self):
        return "month"


Month = _Month()

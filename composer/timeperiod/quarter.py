from __future__ import absolute_import
from .utils import get_next_day
from .base import Period, PeriodAdvanceCriteria
from .day import Day
from .month import Month


class _Quarter(Period):

    duration = 3 * 4 * 7 * 24 * 60 * 60

    def advance_criteria_met(self, planner, now):
        next_day = get_next_day(planner.date)
        month = next_day.strftime("%B")
        day_criteria_met = Day.advance_criteria_met(planner, now)
        if day_criteria_met == PeriodAdvanceCriteria.PlannerInFuture:
            return PeriodAdvanceCriteria.PlannerInFuture
        elif Month.advance_criteria_met(planner, now) and month.lower() in (
            "january",
            "april",
            "july",
            "october",
        ):
            return PeriodAdvanceCriteria.Satisfied

    def get_name(self):
        return "quarter"


Quarter = _Quarter()

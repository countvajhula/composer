from __future__ import absolute_import
from .base import Period, PeriodAdvanceCriteria


class _Day(Period):

    duration = 24 * 60 * 60

    def advance_criteria_met(self, planner, now):
        today = now.date()
        if planner.date < today:
            return PeriodAdvanceCriteria.Satisfied
        if planner.date == today:
            if now.hour >= 18:
                return PeriodAdvanceCriteria.Satisfied
            else:
                # current day still in progress
                return PeriodAdvanceCriteria.DayStillInProgress
        else:
            # planner is in the future
            return PeriodAdvanceCriteria.PlannerInFuture

    def get_logfile(self, planner):
        return planner.dayfile

    def get_name(self):
        return "day"


Day = _Day()

from ..errors import PlannerIsInTheFutureError
from .utils import get_next_day
from .base import Period
from .day import Day
from .month import Month


class _Quarter(Period):

    duration = 3 * 4 * 7 * 24 * 60 * 60

    def advance_criteria_met(self, planner, now):
        next_day = get_next_day(planner.date)
        month = next_day.strftime("%B")
        try:
            Day.advance_criteria_met(planner, now)
        except PlannerIsInTheFutureError:
            raise
        if Month.advance_criteria_met(planner, now) and month.lower() in (
            "january",
            "april",
            "july",
            "october",
        ):
            return True
        else:
            return False

    def get_name(self):
        return "quarter"


Quarter = _Quarter()

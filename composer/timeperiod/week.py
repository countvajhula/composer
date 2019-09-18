import calendar

from ..errors import PlannerIsInTheFutureError
from .base import Period
from .day import Day
from .month import Month

MIN_WEEK_LENGTH = 5


class _Week(Period):

    duration = 7 * 24 * 60 * 60

    def advance_criteria_met(self, planner_date, now):
        # note that these dates are ~next~ day values
        dow = planner_date.strftime("%A")
        year = planner_date.year
        try:
            day_criteria_met = Day.advance_criteria_met(planner_date, now)
        except PlannerIsInTheFutureError:
            raise
        if Month.advance_criteria_met(planner_date, now) or (
            day_criteria_met
            and dow.lower() == "saturday"
            and planner_date.day >= MIN_WEEK_LENGTH
            and calendar.monthrange(year, planner_date.month)[1]
            - planner_date.day
            >= MIN_WEEK_LENGTH
        ):
            return True
        else:
            return False

    def get_name(self):
        return "week"


Week = _Week()

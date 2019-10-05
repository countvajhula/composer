import datetime
from datetime import timedelta

from ..errors import PlannerIsInTheFutureError
from .base import Period


class _Day(Period):

    duration = 24 * 60 * 60

    def advance_criteria_met(self, to_date):
        """ Have criteria for advancement to the next day been met?

        :param :class:`datetime.date` to_date: The date to advance to
        :returns bool: Whether the criteria have been met
        """
        now = datetime.datetime.now()
        today = now.date()
        tomorrow = today + timedelta(days=1)

        if to_date <= today:
            return True
        elif to_date == tomorrow:
            if now.hour >= 18:
                return True
            else:
                # current day still in progress
                return False
        else:
            # planner is in the future
            raise PlannerIsInTheFutureError("Planner is in the future!")

    def get_name(self):
        return "day"


Day = _Day()

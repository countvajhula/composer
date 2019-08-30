import abc

from datetime import datetime

from ..config import (
    DEFAULT_BULLET_CHARACTER,
    DEFAULT_SCHEDULE,
    LOGFILE_CHECKING,
)
from ..errors import LogfileNotCompletedError, PlannerIsInTheFutureError
from ..timeperiod import get_next_day, get_next_period, Zero, Year

from .filesystem import templates

ABC = abc.ABCMeta("ABC", (object,), {})  # compatible with Python 2 *and* 3


class PlannerBase(ABC):
    date = None
    tomorrow_checking = LOGFILE_CHECKING["STRICT"]
    logfile_completion_checking = LOGFILE_CHECKING["STRICT"]
    preferred_bullet_char = DEFAULT_BULLET_CHARACTER
    schedule = DEFAULT_SCHEDULE
    week_theme = None
    jumping = False

    def set_preferences(self, preferences=None):
        if preferences:
            self.schedule = preferences.get("schedule", DEFAULT_SCHEDULE)
            self.preferred_bullet_char = preferences.get(
                "bullet_character", DEFAULT_BULLET_CHARACTER
            )
            self.jumping = preferences.get("jump", False)

            self.logfile_completion_checking = preferences.get(
                "logfile_completion_checking", LOGFILE_CHECKING['STRICT']
            )
            self.tomorrow_checking = preferences.get(
                "tomorrow_checking", LOGFILE_CHECKING['STRICT']
            )
            if self.jumping:
                # jumping overrides preferences for logfile checking
                self.logfile_completion_checking = LOGFILE_CHECKING["LAX"]
                self.tomorrow_checking = LOGFILE_CHECKING["LAX"]
            self.week_theme = preferences.get("week_theme")

    @abc.abstractmethod
    def construct(self, location=None):
        raise NotImplementedError

    @abc.abstractmethod
    def get_agenda(self, period):
        raise NotImplementedError

    @abc.abstractmethod
    def update_agenda(self, period, agenda):
        raise NotImplementedError

    @abc.abstractmethod
    def check_log_completion(self, period):
        raise NotImplementedError

    @abc.abstractmethod
    def schedule_tasks(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_due_tasks(self, for_day):
        raise NotImplementedError

    def advance_period(self, current_period=None, next_day=None):
        """ Recursive function to advance planner by day, week, month, quarter, or year
        as the case may be.
        """
        if not current_period:
            current_period = Zero
        if not next_day:
            next_day = get_next_day(self.date)  # the new day to advance to
        if current_period == Year:
            # base case
            return current_period

        next_period = get_next_period(current_period)
        try:
            criteria_met = next_period.advance_criteria_met(self, self.now)
        except PlannerIsInTheFutureError:
            raise

        if criteria_met:
            if self.logfile_completion_checking == LOGFILE_CHECKING[
                "STRICT"
            ] and not self.check_log_completion(next_period):
                periodstr = next_period.get_name()
                msg = (
                    "Looks like you haven't completed your %s's log."
                    " Would you like to do that now?" % periodstr
                )
                raise LogfileNotCompletedError(msg, periodstr)
            templates.write_new_template(self, next_period, next_day)

            return self.advance_period(next_period)
        else:
            # did not advance beyond current period. If we have advanced
            # at all (e.g. a smaller period), we still want to
            # update the existing template for the encompassing period
            if current_period > Zero:
                templates.write_existing_template(self, next_period, next_day)
            return current_period

    @abc.abstractmethod
    def advance(self, now=None, simulate=False):
        """ Advance planner state to next day, updating week and month info
        as necessary. 'now' arg used only for testing
        """
        if not now:
            now = datetime.now()

        next_day = get_next_day(self.date)  # the new day to advance to

        self.now = now

        self.schedule_tasks()

        status = self.advance_period(Zero, next_day)
        if status > Zero:
            self.date = next_day
        return status

    @abc.abstractmethod
    def save(self):
        raise NotImplementedError

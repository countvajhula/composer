import abc

from datetime import datetime

from ..config import (
    DEFAULT_BULLET_CHARACTER,
    DEFAULT_SCHEDULE,
    LOGFILE_CHECKING,
)
from ..errors import LogfileNotCompletedError, PlannerIsInTheFutureError
from ..timeperiod import get_next_day, get_next_period, Zero, Month, Year

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

    def cascade_agenda(self, period):
        """ Append the current period's agenda to the next period's
        agenda. This 'cascades' actvities up through encompassing
        time periods, since something worked on on a given day is also
        worked on during the containing periods (like the week).
        """

        # TODO: at the moment this doesn't do any parsing or deduplication of
        # tasks. As a result, containing periods contain the same tasks over
        # and over again, and often without any changes or only minor
        # changes. While the feature is somewhat useful for grep style
        # searching in order to find when things were done, it is minimally
        # functional and not suitable for perusing. This should be improved,
        # but for now, to minimize unreasonably large file sizes from
        # duplication, limit cascade to only day->week->month

        # TODO: this is getting overwritten by write_existing_template
        if period < Month:
            agenda = self.get_agenda(period)
            next_period = get_next_period(period)
            if agenda:
                self.update_agenda(next_period, agenda)

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
                msg = (
                    "Looks like you haven't completed your %s's log."
                    " Would you like to do that now?" % next_period
                )
                raise LogfileNotCompletedError(msg, next_period)
            # we need to do the cascade before writing the new template since
            # at that stage the period logfile would reflect the newly written
            # one rather than the closing state of the one at the end of the
            # period in question.
            # Also note we are cascading the agenda for the *next* period to
            # the still-higher period
            #
            # TODO: it would be cleaner if we could handle this as part of
            # non-advancement of the next period, i.e. as part of modifying the
            # existing template at that stage (the else clause below). In order
            # to do this cleanly, it could make sense to define a notion of a
            # "transaction" so that planner attributes are never mutated
            # directly -- instead, the proposed changes are added to an active
            # "transaction" which is reasoned about at each stage and committed
            # at the end.  this way, we could use either the existing or the
            # updated versions of any document at any stage, depending on what
            # needs to be done, and wouldn't be tied to doing the cascade prior
            # to new template generation here.
            # Consider using the python transaction library to keep these
            # transaction-specific semantics streamlined
            self.cascade_agenda(next_period)
            self.write_new_template(next_period, next_day)

            return self.advance_period(next_period)
        else:
            # did not advance beyond current period. If we have advanced
            # at all (e.g. a smaller period), we still want to
            # update the existing template for the encompassing period
            if current_period > Zero:
                self.write_existing_template(next_period, next_day)
            return current_period

    @abc.abstractmethod
    def advance(self, now=None):
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
    def save(self, period=Year):
        raise NotImplementedError

import abc

from datetime import datetime

from ..config import (
    DEFAULT_BULLET_CHARACTER,
    DEFAULT_SCHEDULE,
    LOGFILE_CHECKING,
)
from ..errors import (
    LogfileNotCompletedError,
    PlannerIsInTheFutureError,
    MissingThemeError,
)
from ..timeperiod import (
    get_next_day,
    get_next_period,
    Zero,
    Day,
    Week,
    Month,
    Year,
)
from ..utils import display_message

ABC = abc.ABCMeta("ABC", (object,), {})  # compatible with Python 2 *and* 3


class PlannerBase(ABC):
    date = None
    tomorrow_checking = LOGFILE_CHECKING["STRICT"]
    logfile_completion_checking = LOGFILE_CHECKING["STRICT"]
    preferred_bullet_char = DEFAULT_BULLET_CHARACTER
    schedule = DEFAULT_SCHEDULE
    week_theme = None
    jumping = False

    def set_preferences(self, preferences):
        """ Set planner preferences, e.g. schedule to operate on, preferred
        parameters for log file formatting, etc.

        :param dict preferences: A dictionary of user preferences, e.g. read
            from a config location on disk
        """
        self.schedule = preferences.get("schedule", self.schedule)
        self.preferred_bullet_char = preferences.get(
            "bullet_character", self.preferred_bullet_char
        )
        self.jumping = preferences.get("jump", self.jumping)

        self.logfile_completion_checking = preferences.get(
            "logfile_completion_checking", self.logfile_completion_checking
        )
        self.tomorrow_checking = preferences.get(
            "tomorrow_checking", self.tomorrow_checking
        )
        self.week_theme = preferences.get("week_theme", self.week_theme)
        if self.jumping:
            # jumping overrides preferences for logfile checking
            self.logfile_completion_checking = LOGFILE_CHECKING["LAX"]
            self.tomorrow_checking = LOGFILE_CHECKING["LAX"]

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

    @abc.abstractmethod
    def get_tasks_for_tomorrow(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_todays_unfinished_tasks(self):
        raise NotImplementedError

    @abc.abstractmethod
    def create_log(self, period, next_day):
        raise NotImplementedError

    @abc.abstractmethod
    def update_log(self, period, next_day):
        raise NotImplementedError

    def cascade_agenda(self, period):
        """ Append the current period's agenda to the next higher period's
        agenda.  This 'cascades' actvities up through encompassing time
        periods, since something worked on on a given day is also worked on
        during the containing periods (like the week).

        :param :class:`~composer.timeperiod.Period` period: Current time period
            (e.g. Day) whose agenda will be cascaded up to the next one
            (e.g. Week)
        """

        # TODO: at the moment this doesn't do any parsing or deduplication of
        # tasks. As a result, containing periods contain the same tasks over
        # and over again, and often without any changes or only minor
        # changes. While the feature is somewhat useful for grep style
        # searching in order to find when things were done, it is minimally
        # functional and not suitable for perusing. This should be improved,
        # but for now, to minimize unreasonably large file sizes from
        # duplication, limit cascade to only day->week->month

        agenda = self.get_agenda(period)
        next_period = get_next_period(period)
        if agenda:
            self.update_agenda(next_period, agenda)

    def end_period(self, period):
        """ Perform any tasks needed to close out a period.
        At the moment this cascades the period's agenda to the containing
        period's agenda, checks log completion, and processes any tasks that
        have been scheduled / marked as blocked.

        :param :class:`~composer.timeperiod.Period` period: The period to end
        """
        # we need to do the cascade before writing the new template for the
        # period since at that stage the logfile attribute would reflect the
        # newly written one rather than the closing state of the one at the end
        # of the period in question.
        display_message(
            "Performing bookkeeping for {period}'s end...".format(
                period=period
            )
        )
        if not self.check_log_completion(period):
            msg = (
                "Looks like you haven't completed your %s's log."
                " Would you like to do that now?" % period
            )
            raise LogfileNotCompletedError(msg, period)

        if period == Day:
            self.schedule_tasks()

        if period < Month:
            # limit to month to minimize extravagant duplication
            self.cascade_agenda(period)

    def begin_period(self, period, next_day):
        """ Perform any tasks needed to begin a new period.
        At the moment this just creates a log for the new period.

        :param :class:`~composer.timeperiod.Period` period: The period to begin
        """
        display_message("Beginning new {period}...".format(period=period))
        if period == Week and self.week_theme is None:
            # it would be an empty string (rather than None) if the user
            # was asked about it but chose to enter nothing
            raise MissingThemeError("Missing theme for the week!", period=Week)
        self.create_log(period, next_day)

    def continue_period(self, period, next_day):
        """ Perform any tasks needed to continue an existing period in light of
        the advance of a contained period.  At the moment this just updates the
        existing log for the period, e.g. to include a link to the newly
        created logfile for the contained period.

        :param :class:`~composer.timeperiod.Period` period: The period to
            continue
        """
        self.update_log(period, next_day)

    def advance_period(self, current_period=None, next_day=None):
        """ Recursive function to advance planner by day, week, month, quarter,
        or year as the case may be.

        :param :class:`~composer.timeperiod.Period` current_period: The period
            we have advanced up to thus far.
        :param :class:`datetime.date` next_day: The day we are advancing to
            (which may entail an advancement of multiple encompassing periods)
        :returns :class:`~composer.timeperiod.Period`: The highest period
            advanced
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
            criteria_met = next_period.advance_criteria_met(
                self.date, self.now
            )
        except PlannerIsInTheFutureError:
            raise

        if criteria_met:
            self.end_period(next_period)
            self.begin_period(next_period, next_day)

            return self.advance_period(next_period, next_day)
        else:
            # did not advance beyond current period. If we have advanced
            # at all (e.g. a smaller period), we still want to
            # update the existing template for the encompassing period
            if current_period > Zero:
                self.continue_period(next_period, next_day)
            return current_period

    def advance(self, now=None):
        """ Advance planner state to next day, updating week and month info
        as necessary. 'now' arg used only for testing
        If successful, the date (self.date) is advanced to the next day

        Note that for the filesystem planner, after the advance() returns, the
        file handles will have been updated to the (possibly new) buffers (but
        still not persisted until save() is called).

        :param :class:`datetime.datetime` now: The time to use as the current
            real world time
        :returns :class:`~composer.timeperiod.Period`: The highest period
            advanced
        """
        if not now:
            now = datetime.now()

        next_day = get_next_day(self.date)  # the new day to advance to

        self.now = now

        status = self.advance_period(Zero, next_day)
        if status > Zero:
            self.date = next_day
        return status

    @abc.abstractmethod
    def save(self, period=Year):
        raise NotImplementedError

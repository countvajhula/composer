import abc

import datetime

from ..config import (
    DEFAULT_BULLET_CHARACTER,
    DEFAULT_SCHEDULE,
    LOGFILE_CHECKING,
)
from ..errors import (
    AgendaNotReviewedError,
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
    Year,
)
from ..utils import display_message

ABC = abc.ABCMeta("ABC", (object,), {})  # compatible with Python 2 *and* 3


class PlannerBase(ABC):
    date = None
    logfile_completion_checking = LOGFILE_CHECKING["STRICT"]
    preferred_bullet_char = DEFAULT_BULLET_CHARACTER
    schedule = DEFAULT_SCHEDULE
    week_theme = None
    jump_to_date = None
    next_day_planner = None
    agenda_reviewed = Zero
    tasklist = None

    def __init__(self, location, tasklist):
        self.tasklist = tasklist

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
        if preferences.get("jump"):
            today = datetime.date.today()
            self.set_jump_date(today)

        self.logfile_completion_checking = preferences.get(
            "logfile_completion_checking", self.logfile_completion_checking
        )
        self.week_theme = preferences.get("week_theme", self.week_theme)
        self.agenda_reviewed = preferences.get(
            "agenda_reviewed", self.agenda_reviewed
        )
        if self.jump_to_date:
            # jumping overrides preferences for logfile checking
            # TODO: not needed anymore?
            self.logfile_completion_checking = LOGFILE_CHECKING["LAX"]

    def set_jump_date(self, date):
        """ Set the date to jump to. If this date is in the past (relative to
        planner state), then it is ignored.

        :param :class:`datetime.date` date: The date to jump to
        """
        self.jump_to_date = date if date > self.date else None

    @abc.abstractmethod
    def construct(self, location=None, tasklist=None):
        raise NotImplementedError

    def next_day(self):
        return (
            self.jump_to_date if self.jump_to_date else get_next_day(self.date)
        )

    @abc.abstractmethod
    def get_log(self, for_day, period):
        raise NotImplementedError

    @abc.abstractmethod
    def get_agenda(self, period, complete=None):
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
    def get_todays_unfinished_tasks(self):
        raise NotImplementedError

    @abc.abstractmethod
    def create_log(self, period, for_day):
        raise NotImplementedError

    @abc.abstractmethod
    def update_log(self, period, for_day):
        raise NotImplementedError

    def _cascade_up(self, period, complete):
        agenda = self.get_agenda(period, complete)

        next_period = get_next_period(period)
        if agenda:
            self.update_agenda(next_period, agenda)

    def cascade_agenda(self, period):
        """ Append the specified period's agenda to the next higher period's
        agenda.  This 'cascades' actvities up through encompassing time
        periods, since something worked on on a given day is also worked on
        during the containing periods (like the week).

        :param :class:`~composer.timeperiod.Period` period: Current time period
            (e.g. Day) whose agenda will be cascaded up to the next one
            (e.g. Week)
        """
        if period > Day:
            # cascade the incomplete agenda items from the last lesser
            # contained period (complete have already been cascaded by this
            # point)
            # TODO: non-task entries would be out of context if not moved
            # wholesale with all tasks
            lower_period = get_next_period(period, decreasing=True)
            self._cascade_up(lower_period, complete=False)
        if period < Year:
            self._cascade_up(period, complete=True)

    def end_period(self, period):
        """ Perform any tasks needed to close out a period.
        At the moment this cascades the period's agenda to the containing
        period's agenda, checks log completion, and processes any tasks that
        have been scheduled / marked as blocked.

        :param :class:`~composer.timeperiod.Period` period: The period to end
        """
        display_message(
            "Performing bookkeeping for {period}'s end".format(period=period),
            interactive=True,
        )
        if not self.check_log_completion(period):
            msg = (
                "Looks like you haven't completed your %s's log."
                " Would you like to do that now?" % period
            )
            raise LogfileNotCompletedError(msg, period)

        if period == Day:
            self.schedule_tasks()

        self.cascade_agenda(period)

    def begin_period(self, period, for_day):
        """ Perform any tasks needed to begin a new period.
        At the moment this just creates a log for the new period.

        :param :class:`~composer.timeperiod.Period` period: The period to begin
        :param :class:`datetime.date` for_day: The day we are advancing to
        """
        display_message(
            "Beginning new {period}".format(period=str(period).upper()),
            interactive=True,
        )
        self.create_log(period, for_day)
        if self.agenda_reviewed < period:
            if period == Day:
                # show the tentative agenda as constituted by tasks added
                # directly for tomorrow, tasks carrying over from today, and
                # scheduled tasks becoming due tomorrow. It may make things
                # simpler if we just do all of those things as part of EOP
                # activities and constitute them all in the TOMORROW section of
                # the tasklist, for review by the user. Then, it can be treated
                # the same as any other period for review here. On the other
                # hand, this would imply that the disk state is being mutated
                # by planner logic prior to saving the "pre-advance" state in
                # git, which may be unsafe
                agenda = self.next_day_planner.get_agenda(period)
            else:
                # show the agenda as indicated for the period in the tasklist
                agenda, _ = self.tasklist.get_tasks(period)
            raise AgendaNotReviewedError(
                "Agenda for {period} not reviewed!".format(period=period),
                period=period,
                agenda=agenda,
            )
        if period == Week and self.week_theme is None:
            # it would be an empty string (rather than None) if the user
            # was asked about it but chose to enter nothing
            raise MissingThemeError(
                "Missing theme for the {period}!".format(period=period),
                period=period,
            )

    def continue_period(self, period, for_day):
        """ Perform any tasks needed to continue an existing period in light of
        the advance of a contained period.  At the moment this just updates the
        existing log for the period, e.g. to include a link to the newly
        created logfile for the contained period.

        :param :class:`~composer.timeperiod.Period` period: The period to
            continue
        :param :class:`datetime.date` for_day: The day we are advancing to
        """
        self.update_log(period, for_day)

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
            next_day = self.next_day()  # the new day to advance to
        if current_period == Year:
            # base case
            return current_period

        next_period = get_next_period(current_period)
        try:
            criteria_met = next_period.advance_criteria_met(next_day)
        except PlannerIsInTheFutureError:
            raise

        if next_period > Day and not criteria_met:
            # if we are jumping, then it's possible that even if calendar-based
            # period boundary criteria are not met, that it still represents an
            # advance of the concerned period since we may not already have a
            # log file tracking the target date
            is_date_tracked = self.get_log(next_day, next_period)
            if not is_date_tracked:
                criteria_met = True

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

    def advance(self):
        """ Advance planner state to next day, updating week and month info
        as necessary.
        If successful, the date (self.date) is advanced to the next day

        Note that for the filesystem planner, after the advance() returns, the
        file handles will have been updated to the (possibly new) buffers (but
        still not persisted until save() is called).

        :returns :class:`~composer.timeperiod.Period`: The highest period
            advanced
        """
        next_day = self.next_day()  # the new day to advance to

        # essentially create a clone of the planner to be populated
        # for the next day
        self.next_day_planner = self.__class__()
        self.next_day_planner.construct(self.location)
        # both current and next day planner instances use
        # the same tasklist instance
        self.next_day_planner.tasklist = self.tasklist
        self.next_day_planner.date = next_day

        status = self.advance_period(Zero, next_day)
        if status == Zero:
            self.next_day_planner = None
        return status, self.next_day_planner

    @abc.abstractmethod
    def is_ok_to_advance(self, period=Year):
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, period=Year):
        raise NotImplementedError


class TasklistBase(ABC):
    @abc.abstractmethod
    def get_tasks(self, period):
        raise NotImplementedError

    @abc.abstractmethod
    def get_due_tasks(self, for_day):
        raise NotImplementedError

    @abc.abstractmethod
    def get_tasks_for_tomorrow(self):
        raise NotImplementedError

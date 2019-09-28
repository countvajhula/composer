import os

from ..base import PlannerBase
from ...config import LOGFILE_CHECKING
from ...timeperiod import (
    get_next_period,
    Day,
    Week,
    Month,
    Quarter,
    Year,
    Zero,
)
from ...errors import (
    BlockedTaskNotScheduledError,
    LogfileLayoutError,
    SchedulingDateError,
    TasklistLayoutError,
    TomorrowIsEmptyError,
)
from ...utils import display_message
from .scheduling import (
    check_logfile_for_errors,
    check_scheduled_section_for_errors,
    sanitize_entry,
    SCHEDULED_DATE_PATTERN,
    string_to_date,
)
from .templates import get_template
from .interface import ensure_file_does_not_exist

# should minimize use of low-level (lower than "entry" level) primitives in
# this file. if necessary, provide duplicate versions of functions at the
# relevant abstraction level and have those internally map to and from the
# lower abstraction level to leverage the low level operations at the higher
# level in a formal way
from .primitives import (
    is_scheduled_task,
    is_undone_task,
    is_wip_task,
    get_log_filename,
    parse_task,
    make_file,
    full_file_path,
    read_file,
    write_file,
    add_to_section,
    get_entries,
    entries_to_string,
    partition_entries,
    read_section,
    bare_filename,
)

SCHEDULE_FILE_PREFIX = "Checkpoints"
PLANNERTASKLISTFILE = "TaskList.wiki"
PLANNERDAYTHEMESFILE = "DayThemes.wiki"
PLANNERDAYFILELINK = "currentday"
CHECKPOINTSWEEKFILE = "Checkpoints_Week.wiki"
CHECKPOINTSMONTHFILE = "Checkpoints_Month.wiki"
CHECKPOINTSQUARTERFILE = "Checkpoints_Quarter.wiki"
CHECKPOINTSYEARFILE = "Checkpoints_Year.wiki"
PERIODICYEARLYFILE = "Periodic_Yearly.wiki"
PERIODICQUARTERLYFILE = "Periodic_Quarterly.wiki"
PERIODICMONTHLYFILE = "Periodic_Monthly.wiki"
PERIODICWEEKLYFILE = "Periodic_Weekly.wiki"
PERIODICDAILYFILE = "Periodic_Daily.wiki"


class FilesystemPlanner(PlannerBase):
    _tasklistfile = None
    _daythemesfile = None
    _dayfile = None
    _weekfile = None
    _monthfile = None
    _quarterfile = None
    _yearfile = None
    _checkpoints_weekday_file = None
    _checkpoints_weekend_file = None
    _checkpoints_week_file = None
    _checkpoints_month_file = None
    _checkpoints_quarter_file = None
    _checkpoints_year_file = None
    _periodic_day_file = None
    _periodic_week_file = None
    _periodic_month_file = None
    _periodic_quarter_file = None
    _periodic_year_file = None

    def __init__(self, location=None):
        self.construct(location)

    # use 'getters' and 'setters' for file attributes so that any state changes
    # to their values (e.g. "head" position after reading the file's contents)
    # are contained within the client code and not reflected on the planner
    # instance unless it is explicitly modified via a setter

    @property
    def tasklistfile(self):
        return make_file(self._tasklistfile.getvalue())

    @tasklistfile.setter
    def tasklistfile(self, value):
        self._tasklistfile = value

    @property
    def daythemesfile(self):
        return make_file(self._daythemesfile.getvalue())

    @daythemesfile.setter
    def daythemesfile(self, value):
        self._daythemesfile = value

    @property
    def dayfile(self):
        return make_file(self._dayfile.getvalue())

    @dayfile.setter
    def dayfile(self, value):
        self._dayfile = value

    @property
    def weekfile(self):
        return make_file(self._weekfile.getvalue())

    @weekfile.setter
    def weekfile(self, value):
        self._weekfile = value

    @property
    def monthfile(self):
        return make_file(self._monthfile.getvalue())

    @monthfile.setter
    def monthfile(self, value):
        self._monthfile = value

    @property
    def quarterfile(self):
        return make_file(self._quarterfile.getvalue())

    @quarterfile.setter
    def quarterfile(self, value):
        self._quarterfile = value

    @property
    def yearfile(self):
        return make_file(self._yearfile.getvalue())

    @yearfile.setter
    def yearfile(self, value):
        self._yearfile = value

    def _logfile_attribute(self, period):
        """ A helper to get the name of the attribute on the planner instance
        corresponding to the log file for the given period.

        :param :class:`~composer.timeperiod.Period` period: A time period
        :returns str: The attribute name
        """
        if period == Day:
            attr = 'dayfile'
        elif period == Week:
            attr = 'weekfile'
        elif period == Month:
            attr = 'monthfile'
        elif period == Quarter:
            attr = 'quarterfile'
        elif period == Year:
            attr = 'yearfile'
        elif period == Zero:
            attr = ''
        return attr

    def _get_logfile(self, period):
        """ Time period-agnostic "getter" for the concerned logfile attribute.
        Note: This would be unnecessary if each planner instance was only
        concerned with a specific period rather than all periods.

        :param :class:`~composer.timeperiod.Period` period: A time period
        :returns :class:`io.StringIO`: A file corresponding to the log for
            the given time period
        """
        log_attr = self._logfile_attribute(period)
        log = getattr(self, log_attr)
        return log

    def _update_logfile(self, period, contents):
        """ Time period-agnostic "setter" for the concerned logfile attribute.
        Note: This would be unnecessary if each planner instance was only
        concerned with a specific period rather than all periods.

        :param :class:`~composer.timeperiod.Period` period: A time period
        :param str contents: The new contents of the log file
        """
        log_attr = self._logfile_attribute(period)
        if log_attr:
            setattr(self, log_attr, make_file(contents))

    def _update_tasklist(self, new_tasklist):
        """ A setter to update the tasklist on both this planner instance
        as well as the one for the next day since any changes to the tasklist
        should be retained on the next day's planner instance. Kind of hacky,
        and probably implies that the tasklist should be managed outside this
        period-centric notion of a planner, or even better, that the tasklist
        should be incorporated into time periods as part of "composing" them.

        :param :class:`io.StringIO` new_tasklist: The new tasklist
        """
        self.tasklistfile = new_tasklist
        self.next_day_planner.tasklistfile = new_tasklist

    def _get_date(self):
        """ Get date from planner's current state on disk.
        The current date is tracked using a symbolic link which points to the
        latest daily logfile generated.
        """
        plannerdatefn = full_file_path(
            PLANNERDAYFILELINK, root=self.location, dereference=True
        )
        datestr = bare_filename(plannerdatefn)
        plannerdate, _ = string_to_date(datestr)
        return plannerdate

    def construct(self, location=None):
        """ Construct a planner object from a filesystem representation.

        :param str location: Filesystem path to planner wiki
        """
        # use a bunch of StringIO buffers for the Planner object
        # populate them here from real files
        if location is None:
            # needed for tests atm -- eventually make location a required arg
            return
        self.location = location
        self.date = self._get_date()
        # populate attributes on planner object from files on disk
        planner_files = {
            'tasklistfile': PLANNERTASKLISTFILE,
            'daythemesfile': PLANNERDAYTHEMESFILE,
            'dayfile': get_log_filename(self.date, Day),
            'weekfile': get_log_filename(Week.get_start_date(self.date), Week),
            'monthfile': get_log_filename(
                Month.get_start_date(self.date), Month
            ),
            'quarterfile': get_log_filename(
                Quarter.get_start_date(self.date), Quarter
            ),
            'yearfile': get_log_filename(Year.get_start_date(self.date), Year),
            # daily, weekly, monthly checkpoints
            'checkpoints_weekday_file': "{}_Weekday_{}.wiki".format(
                SCHEDULE_FILE_PREFIX, self.schedule.capitalize()
            ),
            'checkpoints_weekend_file': "{}_Weekend_{}.wiki".format(
                SCHEDULE_FILE_PREFIX, self.schedule.capitalize()
            ),
            'checkpoints_week_file': CHECKPOINTSWEEKFILE,
            'checkpoints_month_file': CHECKPOINTSMONTHFILE,
            'checkpoints_quarter_file': CHECKPOINTSQUARTERFILE,
            'checkpoints_year_file': CHECKPOINTSYEARFILE,
            # periodic items
            'periodic_day_file': PERIODICDAILYFILE,
            'periodic_week_file': PERIODICWEEKLYFILE,
            'periodic_month_file': PERIODICMONTHLYFILE,
            'periodic_quarter_file': PERIODICQUARTERLYFILE,
            'periodic_year_file': PERIODICYEARLYFILE,
        }
        for attr, filename in planner_files.items():
            setattr(
                self,
                attr,
                read_file(full_file_path(root=location, filename=filename)),
            )

    def schedule_tasks(self):
        """ Parse tasklist and today's agenda for any (e.g. newly-added)
        scheduled tasks, and move them to the scheduled section of the tasklist
        after converting them to a standard format.  This ignores any tasks
        manually added for tomorrow (these will be handled as tasks for
        tomorrow, not as scheduled tasks).

        If task is marked as scheduled/blocked (i.e. "[o]"), then make sure
        a follow-up date is indicated (via "[$<date>$]") and that it is
        parseable

        Before beginning, this also checks scheduled section in tasklist and
        current day's log file for errors [TODO: move out of this function]
        """
        # TODO: add a "diagnostic" function for sections w/ a checker fn
        # to be applied to entries
        # (can generalize the existing helper for scheduled section)
        # TODO: keep low-level operations contained in utils -- make/extend
        # additional interfaces as needed
        # TODO: these diagnostics are not covered by tests
        display_message("Tracking any newly scheduled tasks...")
        check_scheduled_section_for_errors(self.tasklistfile)
        check_logfile_for_errors(self.dayfile)
        # ignore tasks in tomorrow since actively scheduled by you
        tomorrow, tasklist_no_tomorrow = read_section(
            self.tasklistfile, 'TOMORROW'
        )
        entries = get_entries(tasklist_no_tomorrow)
        tasklist_tasks, tasklist_no_scheduled = partition_entries(
            entries, is_scheduled_task
        )
        # TODO: these interfaces should operate at a high level and translate
        # up/down only at the beginning and end
        tasklist_no_scheduled = make_file(
            entries_to_string(tasklist_no_scheduled)
        )
        day_tasks = get_entries(self.dayfile, of_type=is_scheduled_task)
        tasks = tasklist_tasks + day_tasks
        tasks = [
            (
                sanitize_entry(task, self.date)
                if is_scheduled_task(task)
                else task
            )
            for task in tasks
        ]
        tasks = entries_to_string(tasks)
        new_file = add_to_section(tasklist_no_scheduled, "SCHEDULED", tasks)
        new_file = add_to_section(
            new_file, "TOMORROW", tomorrow.read()
        )  # add tomorrow tasks back
        self._update_tasklist(new_file)

    def get_due_tasks(self, for_day):
        """ Look at the SCHEDULED section of the tasklist and retrieve any
        tasks that are due/overdue for the given day (e.g. tomorrow, if
        preparing tomorrow's agenda). **This also mutates the tasklist by
        removing these tasks from it.**

        This only operates on explicitly scheduled tasks, not tasks manually
        set aside for tomorrow or which may happen to be appropriate for the
        given day as determined in some other way (e.g. periodic tasks).

        Note: task scheduling should already have been performed on relevant
        logfiles (like the previous day's) to migrate those tasks to the
        tasklist.

        :param :class:`datetime.date` for_day: The date to get due tasks for
        :returns str: The tasks that are due
        """

        def is_task_due(task):
            header, _ = parse_task(task)
            if not SCHEDULED_DATE_PATTERN.search(header):
                raise BlockedTaskNotScheduledError(
                    "Scheduled task has no date!" + header
                )
            datestr = SCHEDULED_DATE_PATTERN.search(header).groups()[0]
            try:
                matched_date, _ = string_to_date(datestr)
            except SchedulingDateError:
                raise
            return for_day >= matched_date

        display_message(
            "Checking previously scheduled tasks for any that "
            "are due tomorrow..."
        )
        try:
            scheduled, tasklist_no_scheduled = read_section(
                self.tasklistfile, "scheduled"
            )
        except ValueError:
            raise TasklistLayoutError(
                "No SCHEDULED section found in TaskList!"
            )
        entries = get_entries(scheduled)
        due, not_due = partition_entries(entries, is_task_due)
        due, not_due = map(entries_to_string, (due, not_due))
        new_tasklist = add_to_section(
            tasklist_no_scheduled, 'scheduled', not_due
        )
        self._update_tasklist(new_tasklist)
        return due

    def get_tasks_for_tomorrow(self):
        """ Read the tasklist, parse all tasks under the TOMORROW section
        and return those. **This also mutates the tasklist by removing those
        tasks from it.**

        :returns str: The tasks for tomorrow
        """
        display_message(
            "Moving tasks added for tomorrow over to tomorrow's agenda..."
        )
        try:
            tasks, tasklist_nextday = read_section(
                self.tasklistfile, 'tomorrow'
            )
        except ValueError:
            raise TasklistLayoutError(
                "Error: No 'TOMORROW' section found in your tasklist!"
                " Please add one and try again."
            )
        if (
            tasks.getvalue() == ""
            and self.tomorrow_checking == LOGFILE_CHECKING["STRICT"]
        ):
            raise TomorrowIsEmptyError(
                "The tomorrow section is blank. Do you want to add"
                " some tasks for tomorrow?"
            )
        self._update_tasklist(tasklist_nextday)
        return tasks.read()

    def get_todays_unfinished_tasks(self):
        """ Get tasks from today's agenda that are either undone or in
        progress.

        :returns str: Unfinished tasks from today's log file
        """
        display_message(
            "Carrying over any unfinished tasks from today"
            " to tomorrow's agenda..."
        )
        try:
            tasks, _ = read_section(self.dayfile, 'agenda')
        except ValueError:
            raise LogfileLayoutError(
                "No AGENDA section found in today's log file!"
                " Add one and try again."
            )

        def is_unfinished(entry):
            return is_undone_task(entry) or is_wip_task(entry)

        tasks = entries_to_string(get_entries(tasks, is_unfinished))

        return tasks

    def create_log(self, period, next_day):
        """ Create a new log for the specified period and associate it with the
        current Planner instance. **This updates the logfile attribute
        corresponding to the period in question to the newly created logical
        file.**

        :param :class:`~composer.timeperiod.Period` period: The period for
            which to create the log file
        :param :class:`dateime.date` next_day: The date for the new log file
        """
        display_message(
            "Creating log file for {period}...".format(period=period)
        )
        scheduled = tomorrow = undone = None
        if period == Day:
            scheduled = self.get_due_tasks(next_day)
            tomorrow = self.get_tasks_for_tomorrow()
            undone = self.get_todays_unfinished_tasks()

        template = get_template(self, period, next_day)
        contents = template.build(
            scheduled=scheduled, tomorrow=tomorrow, undone=undone
        )
        # set the logfile on the next day's planner instance to the
        # newly created file, to be saved later
        log_attr = self._logfile_attribute(period)
        setattr(self.next_day_planner, log_attr, make_file(contents))

    def update_log(self, period, next_day):
        """ Update the existing log for the specified period to account for the
        advancement of a contained period.

        :param :class:`~composer.timeperiod.Period` period: The period for
            which to update the log file
        :param :class:`dateime.date` next_day: The new day in consideration of
            which the log file needs to be updated
        """
        display_message(
            "Updating log file for {period}...".format(period=period)
        )
        template = get_template(self, period, next_day)
        contents = template.update()
        self._update_logfile(period, contents)

    def check_log_completion(self, period):
        """ Check whether the log for a period has been completed. Uses the
        logfile's NOTES section as an indicator of this.

        :param :class:`~composer.timeperiod.Period` period: The period for
            which to check log completion
        :returns bool: Whether the log for the period has been completed
        """
        if self.logfile_completion_checking == LOGFILE_CHECKING["LAX"]:
            return True

        completed = False
        log = self._get_logfile(period)
        try:
            notes, _ = read_section(log, 'notes')
        except ValueError:
            raise LogfileLayoutError(
                "Error: No 'NOTES' section found in your {period} "
                "log file!".format(period=period)
            )
        notes = notes.read()
        if notes.strip("\n ") != "":
            completed = True
        return completed

    def get_agenda(self, period):
        """ Go through logfile and extract all tasks under AGENDA

        :param :class:`~composer.timeperiod.Period` period: Get the agenda
            for this time period
        :returns str: The agenda
        """
        if period is Zero:
            return None
        log = self._get_logfile(period)
        try:
            agenda, _ = read_section(log, 'agenda')
        except ValueError:
            raise LogfileLayoutError(
                "No AGENDA section found in {period} log file!"
                " Add one and try again.".format(period=period)
            )
        agenda = agenda.read()
        return agenda

    def update_agenda(self, period, agenda):
        """ Update the agenda for the given period with the provided agenda by
        appending the new contents to the existing ones.

        :param :class:`~composer.timeperiod.Period` period: Update the agenda
            for this period
        :param str agenda: New contents to be appended to the agenda
        """
        log = self._get_logfile(period)
        try:
            logfile_updated = add_to_section(
                log, 'agenda', agenda, above=False, ensure_separator=True
            )
        except ValueError:
            raise LogfileLayoutError(
                "No AGENDA section found in {period} log file!"
                " Add one and try again.".format(period=period)
            )
        self._update_logfile(period, logfile_updated.getvalue())

    def _get_filename(self, period):
        """ Genenerate a full path to the current log file for a given
        period.  This file need not actually exist on disk yet (e.g. in case we
        have just advanced but haven't saved the files to disk).

        :param :class:`~composer.timeperiod.Period` period: A time period
        :returns str: The path to the log file
        """
        start_date = period.get_start_date(self.date)
        return get_log_filename(start_date, period, root=self.location)

    def is_ok_to_advance(self, period=Year):
        """ A helper to check if any time periods just advanced already have
        log files on disk, which is unexpected and an error. This is only
        appropriate to call after logical advance has occurred (but prior to
        writing to disk).

        :param :class:`~composer.timeperiod.Period` period: A time period
        """
        if period == Zero:
            return
        filename = self._get_filename(period)
        ensure_file_does_not_exist(filename, period)
        self.is_ok_to_advance(get_next_period(period, decreasing=True))

    def _write_log_to_file(self, period):
        """ Write the log for the given period to the filesystem.
        If this represents an advancement of the period in question,
        then also update the 'current' state of the planner on disk
        by updating the relevant symbolic link.
        """
        log = self._get_logfile(period)
        filename = self._get_filename(period)
        # write the file to disk
        write_file(log, filename)

    def _write_files_for_contained_periods(self, period):
        """ Write all log files corresponding to periods contained within
        a given time period.

        :param :class:`~composer.timeperiod.Period` period: A time period
        """
        if period == Zero:
            return
        self._write_log_to_file(period)
        self._write_files_for_contained_periods(
            get_next_period(period, decreasing=True)
        )

    def _update_current_date_link(self):
        """ Update "current" link on disk to the newly created log file
        for the date to which the planner was advanced.
        """
        link_name = PLANNERDAYFILELINK
        filelinkfn = full_file_path(root=self.location, filename=link_name)
        if os.path.islink(filelinkfn):
            os.remove(filelinkfn)
        filename = get_log_filename(self.date, Day)
        os.symlink(
            filename, filelinkfn
        )  # don't need full path in filename since it's relative to the link

    def save(self, period=Year):
        """ Write the planner object to the filesystem.

        :param :class:`~composer.timeperiod.Period` period: The highest period
            advanced -- only log files encompassed by this period will be
            updated. If unspecified, all logfiles will be overwritten.
        """

        # write the logfile for the current period as well as all contained
        # periods, since they are all affected by the advance
        self._write_files_for_contained_periods(period)

        # note that this is being saved both before advance
        # and after advance (redundantly) -- tasklist should be
        # either managed separately, or incorporated into
        # time periods directly as a way of "composing" them
        tasklist_filename = full_file_path(
            root=self.location, filename=PLANNERTASKLISTFILE
        )

        write_file(self.tasklistfile, tasklist_filename)

        self._update_current_date_link()

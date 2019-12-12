import os
from collections import defaultdict

from ..base import PlannerBase, TasklistBase
from ...config import LOGFILE_CHECKING
from ...timeperiod import (
    get_next_period,
    get_time_periods,
    Day,
    Week,
    Month,
    Quarter,
    Year,
    Zero,
    Eternity,
)
from ...errors import LogfileLayoutError, TasklistLayoutError, InvalidDateError
from ...utils import display_message
from .scheduling import (
    check_logfile_for_errors,
    get_due_date,
    standardize_entry_date,
    string_to_date,
)
from .templates import get_template
from .interface import ensure_file_does_not_exist, get_log_for_date

# should minimize use of low-level (lower than "entry" level) primitives in
# this file. if necessary, provide duplicate versions of functions at the
# relevant abstraction level and have those internally map to and from the
# lower abstraction level to leverage the low level operations at the higher
# level in a formal way
from .primitives import (
    is_scheduled_task,
    is_unfinished,
    is_completed,
    is_not_completed,
    get_log_filename,
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
    parse_task,
)

try:  # py3
    FileNotFoundError
except NameError:  # py2
    FileNotFoundError = IOError

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
PERIODIC_FILE_PREFIX = "Periodic"


class FilesystemPlanner(PlannerBase):
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

    def __init__(self, location=None, tasklist=None, preferences=None):
        super(FilesystemPlanner, self).__init__(
            location, tasklist, preferences
        )
        self.construct(location)

    # use 'getters' and 'setters' for file attributes so that any state changes
    # to their values (e.g. "head" position after reading the file's contents)
    # are contained within the client code and not reflected on the planner
    # instance unless it is explicitly modified via a setter

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
            'periodic_day_file': "{}_Daily_{}.wiki".format(
                PERIODIC_FILE_PREFIX, self.schedule.capitalize()
            ),
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

    def get_log(self, for_day, period):
        """ Get the log file responsible for the specified period and date.

        :param :class:`~composer.timeperiod.Period` period: The period for
            which to get the log file
        :param :class:`datetime.date` for_day: The reference date to identify
            the desired log file.
        """
        try:
            log = get_log_for_date(period, for_day, self.location)
        except FileNotFoundError:
            return None
        else:
            return log

    def schedule_tasks(self):
        """ Parse today's agenda for any (e.g. newly-added) scheduled tasks,
        and move them to the appropriate section of the tasklist after
        converting them to a standard format.

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
        display_message("Tracking any newly scheduled tasks", interactive=True)
        check_logfile_for_errors(self.dayfile)

        tasks = get_entries(self.dayfile, of_type=is_scheduled_task)

        tasks = [
            (
                standardize_entry_date(task, self.date)
                if is_scheduled_task(task)
                else task
            )
            for task in tasks
        ]
        # check that any blocked tasks have due dates in the future
        # this is usually because a blocked task became due today and
        # wasn't updated to reflect that it isn't blocked anymore
        # we want to be strict about this case since if left unchanged,
        # it is treated as a "rescheduled" task, i.e. a "completed" task
        # for the purposes of the agenda cascade, which would lead to
        # unnecessary duplication in the log file of the higher period
        # which would show it as being rescheduled every day
        for task in tasks:
            due_date, _ = get_due_date(task, self.date)
            if due_date <= self.date:
                header, _ = parse_task(task)
                raise InvalidDateError(
                    "Due date for blocked task is in the past! If the task "
                    "is no longer blocked, then remove the blocked "
                    "indicator. Otherwise, set a follow-up date in the "
                    "future:\n" + header
                )

        self.tasklist.place_tasks(tasks, self.date)

    def get_todays_unfinished_tasks(self):
        """ Get tasks from today's agenda that are either undone or in
        progress.

        :returns str: Unfinished tasks from today's log file
        """
        display_message(
            "Carrying over any unfinished tasks from today"
            " to tomorrow's agenda",
            interactive=True,
        )
        try:
            tasks, _ = read_section(self.dayfile, 'agenda')
        except ValueError:
            raise LogfileLayoutError(
                "No AGENDA section found in today's log file!"
                " Add one and try again."
            )

        tasks = entries_to_string(get_entries(tasks, is_unfinished))

        return tasks

    def create_log(self, period, for_day):
        """ Create a new log for the specified period and associate it with the
        current Planner instance. **This updates the logfile attribute
        corresponding to the period in question to the newly created logical
        file.**

        :param :class:`~composer.timeperiod.Period` period: The period for
            which to create the log file
        :param :class:`datetime.date` for_day: The reference date which is to
            fall under the purview of the new log file.
        """
        display_message(
            "Creating log file for {period}".format(period=period),
            interactive=True,
        )
        agenda = None
        if period == Day:
            tomorrow = self.tasklist.get_tasks_for_tomorrow()
            undone = self.get_todays_unfinished_tasks()
            agenda = tomorrow + undone

        template = get_template(self, period, for_day)
        contents = template.build(with_agenda=agenda)
        # set the logfile on the next day's planner instance to the
        # newly created file, to be saved later
        log_attr = self._logfile_attribute(period)
        setattr(self.next_day_planner, log_attr, make_file(contents))

    def update_log(self, period, for_day):
        """ Update the existing log for the specified period to account for the
        advancement of a contained period.

        :param :class:`~composer.timeperiod.Period` period: The period for
            which to update the log file
        :param :class:`datetime.date` for_day: The reference date for
            which the corresponding log file needs to be updated
        """
        display_message(
            "Updating log file for {period}".format(period=period),
            interactive=True,
        )
        template = get_template(self, period, for_day)
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

    def get_agenda(self, period, complete=None):
        """ Go through logfile and extract all tasks under AGENDA

        :param :class:`~composer.timeperiod.Period` period: Get the agenda
            for this time period
        :param bool complete: If true, get only completed (e.g. either done,
            invalid or rescheduled) entries; if False, get all other
            (e.g. undone or WIP) entries; if not specified (None), then get the
            full agenda including all entries
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
        if complete:
            of_type = is_completed
        elif complete is False:
            of_type = is_not_completed
        else:
            of_type = None
        agenda = get_entries(agenda, of_type)
        agenda = entries_to_string(agenda)
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

        self._update_current_date_link()


class FilesystemTasklist(TasklistBase):

    _file = None

    section_name = {
        Zero: None,
        Day: "TOMORROW",
        Week: "THIS WEEK",
        Month: "THIS MONTH",
        Quarter: "THIS QUARTER",
        Year: "THIS YEAR",
        Eternity: "SOMEDAY",
    }

    def __init__(self, location=None):
        self.construct(location)

    @property
    def file(self):
        return make_file(self._file.getvalue())

    @file.setter
    def file(self, value):
        self._file = value

    def construct(self, location=None):
        """ Construct a tasklist object from a filesystem representation.

        :param str location: Filesystem path to planner wiki
        """
        if location is None:
            # needed for tests atm -- eventually make location a required arg
            return
        self.location = location
        self.file = read_file(
            full_file_path(root=location, filename=PLANNERTASKLISTFILE)
        )

    def place_tasks(self, scheduled_tasks, reference_date):
        """ Given a list of scheduled tasks, place them in the appropriate
        section of the tasklist relative to the specified reference date. For
        example, a task due on Wednesday would be filed under "this week" in
        the tasklist relative to the Monday of that week (when provided as
        reference date). Note that each section in the tasklist corresponds to
        static date boundaries of the actual "current" periods -- they are
        not "rolling." For instance, on a typical Friday, only tasks due by
        Saturday, i.e. the very next day, would still be filed under "this
        week."

        :param list scheduled_tasks: The list of entries to be placed
        :param :class:`datetime.date` reference_date: The reference date
            for task placement
        """
        # sort them first so that they are placed in chronological order within
        # each section
        scheduled_tasks = sorted(
            scheduled_tasks,
            key=lambda entry: get_due_date(entry, reference_date)[0],
        )
        tasks = defaultdict(lambda: [])
        for entry in scheduled_tasks:
            due_date, _ = get_due_date(entry, reference_date)
            for period in get_time_periods(Day):
                # append and break if within time window
                end_date = period.get_end_date(reference_date)
                if due_date <= end_date:
                    tasks[period].append(entry)
                    break
        for period in get_time_periods(Day):
            tasks_to_add = entries_to_string(tasks[period])
            self.file = add_to_section(
                self.file, self.section_name[period], tasks_to_add, above=False
            )

    def advance(self, to_date):
        """ 'Reverse cascade' tasks from a higher period to an upcoming lower
        period to account for advancement to a future date.

        :param :class:`datetime.date` to_date: The date to advance to
        """
        display_message(
            "Advancing tasklist to check for any upcoming tasks that "
            "are due tomorrow",  # improve
            interactive=True,
        )
        entries = get_entries(self.file)
        scheduled, tasklist_no_scheduled = partition_entries(
            entries, is_scheduled_task
        )
        tasklist_no_scheduled = make_file(
            entries_to_string(tasklist_no_scheduled)
        )
        self.file = tasklist_no_scheduled
        self.place_tasks(scheduled, to_date)

    def standardize_entries(self, reference_date):
        """ Convert all entries in the tasklist to a standard and unambiguous
        (esp. non-relative) date format. This should be done at the time the
        tasks are actually scheduled so that they are disambiguated relative to
        the actual date relative to which the user would have specified them.
        In particular, this should be done prior to 'advance' to any future
        date.

        :param :class:`datetime.date` reference_date: The date relative to
            which entries are to be standardized
        """
        entries = get_entries(self.file)
        entries = [
            standardize_entry_date(entry, reference_date)
            if is_scheduled_task(entry)
            else entry
            for entry in entries
        ]
        self.file = make_file(entries_to_string(entries))

    def get_tasks(self, period):
        """ Read the tasklist, parse all tasks under a specific time period
        and return those, and also return a version of the tasklist file
        with those tasks removed.

        :returns tuple: The tasks under the specified time period (str), and
            the 'complement' tasklist file
        """
        if period == Day:
            section = 'TOMORROW'
        else:
            section = 'THIS ' + str(period).upper()

        try:
            tasks, tasklist_complement = read_section(self.file, section)
        except ValueError:
            raise TasklistLayoutError(
                "Error: No '{section}' section found in your tasklist!"
                " Please add one and try again.".format(section=section)
            )
        return tasks.read(), tasklist_complement

    def get_tasks_for_tomorrow(self):
        """ Read the tasklist, parse all tasks under the TOMORROW section
        and return those. **This also mutates the tasklist by removing those
        tasks from it.**

        :returns str: The tasks for tomorrow
        """
        display_message(
            "Moving tasks added for tomorrow over to tomorrow's agenda",
            interactive=True,
        )
        tasks, tasklist_nextday = self.get_tasks(Day)
        self.file = tasklist_nextday
        return tasks

    def save(self):
        """ Write the tasklist object to the filesystem.
        """

        tasklist_filename = full_file_path(
            root=self.location, filename=PLANNERTASKLISTFILE
        )

        write_file(self.file, tasklist_filename)

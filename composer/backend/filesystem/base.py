import os

from datetime import datetime

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
    LogfileAlreadyExistsError,
    LogfileLayoutError,
    SchedulingDateError,
    TasklistLayoutError,
    TomorrowIsEmptyError,
)
from ...utils import display_message
from .scheduling import (
    check_logfile_for_errors,
    check_scheduled_section_for_errors,
    to_standard_date_format,
    SCHEDULED_DATE_PATTERN,
    get_date_for_schedule_string,
)
from .templates import get_template
from .utils import (
    add_to_section,
    is_scheduled_task,
    full_file_path,
    get_task_items,
    item_list_to_string,
    make_file,
    quarter_for_month,
    partition_items,
    read_file,
    write_file,
    read_section,
)


try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


SCHEDULE_FILE_PREFIX = "Checkpoints"
PLANNERTASKLISTFILE = "TaskList.wiki"
PLANNERDAYTHEMESFILE = "DayThemes.wiki"
PLANNERDAYFILELINK = "currentday"
PLANNERWEEKFILELINK = "currentweek"
PLANNERMONTHFILELINK = "currentmonth"
PLANNERQUARTERFILELINK = "currentquarter"
PLANNERYEARFILELINK = "currentyear"
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

    @property
    def tasklistfile(self):
        return StringIO(self._tasklistfile.getvalue())

    @tasklistfile.setter
    def tasklistfile(self, value):
        self._tasklistfile = value

    @property
    def daythemesfile(self):
        return StringIO(self._daythemesfile.getvalue())

    @daythemesfile.setter
    def daythemesfile(self, value):
        self._daythemesfile = value

    @property
    def dayfile(self):
        return StringIO(self._dayfile.getvalue())

    @dayfile.setter
    def dayfile(self, value):
        self._dayfile = value

    @property
    def weekfile(self):
        return StringIO(self._weekfile.getvalue())

    @weekfile.setter
    def weekfile(self, value):
        self._weekfile = value

    @property
    def monthfile(self):
        return StringIO(self._monthfile.getvalue())

    @monthfile.setter
    def monthfile(self, value):
        self._monthfile = value

    @property
    def quarterfile(self):
        return StringIO(self._quarterfile.getvalue())

    @quarterfile.setter
    def quarterfile(self, value):
        self._quarterfile = value

    @property
    def yearfile(self):
        return StringIO(self._yearfile.getvalue())

    @yearfile.setter
    def yearfile(self, value):
        self._yearfile = value

    def _logfile_attribute(self, period):
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

    def _read_file(self, filename):
        """ Read a file on disk and produce an in-memory logical representation
        of the file. This logical representation will be used for analysis and
        processing so that the actual file on disk isn't affected until any
        such processing is complete.
        """
        contents = read_file(filename)
        return StringIO(contents)

    def _write_file(self, file, filename):
        write_file(file.read(), filename)

    def _get_date(self):
        """ get planner date, currently looks for the file 'currentday',
        if dne throw exception """
        plannerdatefn = full_file_path(
            self.location, PLANNERDAYFILELINK, dereference=True
        )
        pathidx = plannerdatefn.rfind("/")
        datestr = plannerdatefn[
            pathidx + 1 : -5
        ]  # trim path from beginning and '.wiki' from end
        plannerdate = datetime.strptime(datestr, "%B %d, %Y").date()
        return plannerdate

    def construct(self, location=None):
        """ Construct a planner object from a filesystem representation."""
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
            'dayfile': PLANNERDAYFILELINK,
            'weekfile': PLANNERWEEKFILELINK,
            'monthfile': PLANNERMONTHFILELINK,
            'quarterfile': PLANNERQUARTERFILELINK,
            'yearfile': PLANNERYEARFILELINK,
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
                self._read_file(
                    full_file_path(root=location, filename=filename)
                ),
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
        # to be applied to items
        # (can generalize the existing helper for scheduled section)
        # TODO: keep low-level operations contained in utils -- make/extend
        # additional interfaces as needed
        # TODO: these diagnostics are not covered by tests
        display_message("Tracking any newly scheduled tasks...")
        check_scheduled_section_for_errors(self)
        check_logfile_for_errors(self.dayfile)
        # ignore tasks in tomorrow since actively scheduled by you
        tomorrow, tasklist_no_tomorrow = read_section(
            self.tasklistfile, 'TOMORROW'
        )
        task_items = get_task_items(tasklist_no_tomorrow)
        tasklist_tasks, tasklist_no_scheduled = partition_items(
            task_items, is_scheduled_task
        )
        # TODO: these interfaces should operate at a high level and translate
        # up/down only at the beginning and end
        tasklist_no_scheduled = make_file(
            item_list_to_string(tasklist_no_scheduled)
        )
        day_tasks = get_task_items(self.dayfile, of_type=is_scheduled_task)
        tasks = tasklist_tasks + day_tasks
        tasks = [
            (
                to_standard_date_format(task, self.date)
                if is_scheduled_task(task)
                else task
            )
            for task in tasks
        ]
        tasks = item_list_to_string(tasks)
        new_file = add_to_section(tasklist_no_scheduled, "SCHEDULED", tasks)
        new_file = add_to_section(
            new_file, "TOMORROW", tomorrow.read()
        )  # add tomorrow tasks back
        self.tasklistfile = new_file

    def get_due_tasks(self, for_day):
        """ Look at the SCHEDULED section of the tasklist and retrieve any
        tasks that are due/overdue for the given day (e.g. tomorrow, if
        preparing tomorrow's agenda).

        This only operates on explicitly scheduled tasks, not tasks manually
        set aside for tomorrow or which may happen to be appropriate for the
        given day as determined in some other way (e.g. periodic tasks).

        Note: task scheduling should already have been performed on relevant
        logfiles (like the previous day's) to migrate those tasks to the
        tasklist.
        """

        def is_task_due(task):
            if not SCHEDULED_DATE_PATTERN.search(task):
                raise BlockedTaskNotScheduledError(
                    "Scheduled task has no date!" + task
                )
            datestr = SCHEDULED_DATE_PATTERN.search(task).groups()[0]
            try:
                matched_date = get_date_for_schedule_string(datestr)
            except SchedulingDateError:
                raise
            return for_day >= matched_date["date"]

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
        items = get_task_items(scheduled)
        due, not_due = partition_items(items, is_task_due)
        due, not_due = map(item_list_to_string, (due, not_due))
        new_tasklist = add_to_section(
            tasklist_no_scheduled, 'scheduled', not_due
        )
        return due, new_tasklist

    def get_tasks_for_tomorrow(self):
        """ Read the tasklist, parse all tasks under the TOMORROW section
        and return those, and also return a modified tasklist with those
        tasks removed """
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
        return tasks.read(), tasklist_nextday

    def strip_due_tasks_from_tasklist(self, next_day):
        # extract due tasks
        _, tasklistfile = self.get_due_tasks(next_day)
        # extract tomorrow section
        _, tasklistfile = read_section(tasklistfile, 'tomorrow')
        self.tasklistfile = tasklistfile

    def _get_logfile(self, period):
        log_attr = self._logfile_attribute(period)
        log = getattr(self, log_attr)
        return log

    def _update_period_logfile(self, period, contents):
        log_attr = self._logfile_attribute(period)
        if log_attr:
            setattr(self, log_attr, make_file(contents))

    def create_log(self, period, next_day):
        """ Create a new log for the specified period and associate it with the
        current Planner instance. This updates the logfile attribute
        corresponding to the period in question to the newly created logical
        file.
        """
        display_message(
            "Creating log file for {period}...".format(period=period)
        )
        template = get_template(self, period, next_day)
        contents = template.write_new()
        self._update_period_logfile(period, contents)
        if period == Day:
            # this happens independently in creating the template
            # vs here. ideally couple them to avoid bugs related
            # to independent computation of the same thing
            self.strip_due_tasks_from_tasklist(next_day)

    def update_log(self, period, next_day):
        """ Update the existing log for the specified period to account for the
        advancement of a contained period.
        """
        display_message(
            "Updating log file for {period}...".format(period=period)
        )
        template = get_template(self, period, next_day)
        contents = template.write_existing()
        self._update_period_logfile(period, contents)

    def _get_path_for_existing_log(self, period):
        link = self._link_name(period)
        path = full_file_path(
            root=self.location, filename=link, dereference=True
        )
        return path

    def _get_path_for_new_log(self, period):
        (date, month, year) = (
            self.date.day,
            self.date.strftime("%B"),
            self.date.year,
        )

        if period == Day:
            filename = "{month} {date}, {year}.wiki".format(
                month=month, date=date, year=year
            )
        elif period == Week:
            filename = "Week of {month} {date}, {year}.wiki".format(
                month=month, date=date, year=year
            )
        elif period == Month:
            filename = "Month of {month}, {year}.wiki".format(
                month=month, year=year
            )
        elif period == Quarter:
            filename = "{quarter} {year}.wiki".format(
                quarter=quarter_for_month(month), year=year
            )
        elif period == Year:
            filename = "{year}.wiki".format(year=year)
        path = full_file_path(root=self.location, filename=filename)

        return path

    def _log_filename(self, period, is_existing=False):
        """ A time period uniquely maps to a single log file on disk for a
        particular planner instance (which is tied to a wiki root path).  This
        function returns that filename, given a time period. At the moment this
        simply assumes that the reference date is the start of the indicated
        period and constructs a standard filename based on that, but it may be
        desirable to infer the correct filename for the actual or hypothetical
        logfile that would encompass the reference date, based on the current
        period boundary criteria used by the planner.

        :param :class:`composer.timeperiod.Period` period: The time period for
            which to determine a filename
        :param bool is_existing: Whether to return the filename for an existing
            log file for the indicated period. If true, then this simply uses
            the current state on disk and doesn't compute the filename
        """
        if is_existing:
            # use the existing state on disk, don't compute a path
            return self._get_path_for_existing_log(period)
        else:
            # compute a filename based on the reference date
            return self._get_path_for_new_log(period)

    def _link_name(self, period):
        """ The 'current' state of the planner in the filesystem is represented
        as a set of links that point to the current period log files for each
        encompassing time period, i.e. specifically day, week, month, quarter,
        and year, each of which corresponds to a unique "current" logfile on
        disk.  This function returns the symbolic link for the specified time
        period (which points to the current log file for that period).
        """
        if period == Day:
            link = PLANNERDAYFILELINK
        elif period == Week:
            link = PLANNERWEEKFILELINK
        elif period == Month:
            link = PLANNERMONTHFILELINK
        elif period == Quarter:
            link = PLANNERQUARTERFILELINK
        elif period == Year:
            link = PLANNERYEARFILELINK

        return link

    def _write_log_to_file(self, period, is_existing=False):
        """ Write the log for the given period to the filesystem.
        If this represents an advancement of the period in question,
        then also update the 'current' state of the planner on disk
        by updating the relevant symbolic link.

        :param bool is_existing: If true, then write to an existing file.
            Otherwise, write a new file and update the existing link to point
            to it.
        """
        log = self._get_logfile(period)
        filename = self._log_filename(period, is_existing)

        # write the file to disk
        self._write_file(log, filename)

        if not is_existing:
            # update "current" link on disk to the newly created file
            link_name = self._link_name(period)
            filelinkfn = full_file_path(root=self.location, filename=link_name)
            if os.path.islink(filelinkfn):
                os.remove(filelinkfn)
            os.symlink(
                filename[filename.rfind("/") + 1 :], filelinkfn
            )  # remove path from filename so it isn't "double counted"

    def _check_files_for_contained_periods(self, period):
        """ A helper to check if any time periods just advanced already have
        log files on disk, which is unexpected and an error. This is only
        appropriate to call after logical advance has occurred (but prior to
        writing to disk).
        """
        if period == Zero:
            return
        filename = self._log_filename(period)
        if os.path.isfile(filename):
            raise LogfileAlreadyExistsError(
                "New {period} logfile already exists!".format(period=period)
            )
        self._check_files_for_contained_periods(
            get_next_period(period, decreasing=True)
        )

    def check_log_completion(self, period):
        """ Check the logfile's NOTES section as a determination of whether
        the log has been completed """
        log = self._get_logfile(period)
        completed = False
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
        """ Go through logfile and extract all tasks under AGENDA """
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
        self._update_period_logfile(period, logfile_updated.getvalue())

    def _write_files_for_contained_periods(self, period):
        if period == Zero:
            return
        self._write_log_to_file(period)
        self._write_files_for_contained_periods(
            get_next_period(period, decreasing=True)
        )

    def save(self, period=Year):
        """ Write the planner object to the filesystem."""

        # check for possible errors in planner state before making any changes
        # if errors are found, an exception is raised and no changes are made
        self._check_files_for_contained_periods(period)

        # write the logfiles for the current period as well as
        # all contained periods, since they all advance by one
        self._write_files_for_contained_periods(period)

        if period < Year:
            # write the logfile for the encompassing period
            next_period = get_next_period(period)
            # use the pre-advance date to determine the filename for the
            # encompassing period
            self._write_log_to_file(next_period, is_existing=True)
        tasklist_filename = full_file_path(
            root=self.location, filename=PLANNERTASKLISTFILE
        )

        self._write_file(self.tasklistfile, tasklist_filename)

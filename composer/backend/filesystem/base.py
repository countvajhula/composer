import os

from datetime import datetime

from ..base import PlannerBase
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
    SimulationPassedError,
    TasklistLayoutError,
)
from .scheduling import (
    check_logfile_for_errors,
    check_scheduled_section_for_errors,
    to_standard_date_format,
    SCHEDULED_DATE_PATTERN,
    get_date_for_schedule_string,
)
from .utils import (
    add_to_section,
    is_scheduled_task,
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
PATH_SPECIFICATION = "{path}/{filename}"


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
        plannerdatelink = PATH_SPECIFICATION.format(
            path=self.location, filename=PLANNERDAYFILELINK
        )
        plannerdatefn = os.readlink(plannerdatelink)
        pathidx = plannerdatefn.rfind("/")
        datestr = plannerdatefn[
            pathidx + 1 : -5
        ]  # trim path from beginning and '.wiki' from end
        plannerdate = datetime.strptime(datestr, "%B %d, %Y").date()
        return plannerdate

    def construct(self, location=None):
        """ Construct a planner object from a filesystem representation."""
        # CURRENT planner date used here
        if location is None:
            # needed for tests atm -- eventually make location a required arg
            return
        self.location = location
        self.date = self._get_date()
        self.tasklistfile = self._read_file(
            PATH_SPECIFICATION.format(
                path=location, filename=PLANNERTASKLISTFILE
            )
        )
        self.daythemesfile = self._read_file(
            PATH_SPECIFICATION.format(
                path=location, filename=PLANNERDAYTHEMESFILE
            )
        )
        self.dayfile = self._read_file(
            PATH_SPECIFICATION.format(
                path=location, filename=PLANNERDAYFILELINK
            )
        )
        self.weekfile = self._read_file(
            PATH_SPECIFICATION.format(
                path=location, filename=PLANNERWEEKFILELINK
            )
        )
        self.monthfile = self._read_file(
            PATH_SPECIFICATION.format(
                path=location, filename=PLANNERMONTHFILELINK
            )
        )
        self.quarterfile = self._read_file(
            PATH_SPECIFICATION.format(
                path=location, filename=PLANNERQUARTERFILELINK
            )
        )
        self.yearfile = self._read_file(
            PATH_SPECIFICATION.format(
                path=location, filename=PLANNERYEARFILELINK
            )
        )

        # daily, weekly, monthly checkpoints, periodic items
        self.checkpoints_weekday_file = self._read_file(
            "{}/{}_Weekday_{}.wiki".format(
                location, SCHEDULE_FILE_PREFIX, self.schedule.capitalize()
            )
        )
        self.checkpoints_weekend_file = self._read_file(
            "{}/{}_Weekend_{}.wiki".format(
                location, SCHEDULE_FILE_PREFIX, self.schedule.capitalize()
            )
        )
        self.periodic_day_file = self._read_file(
            PATH_SPECIFICATION.format(
                path=location, filename=PERIODICDAILYFILE
            )
        )
        self.checkpoints_week_file = self._read_file(
            PATH_SPECIFICATION.format(
                path=location, filename=CHECKPOINTSWEEKFILE
            )
        )
        self.periodic_week_file = self._read_file(
            PATH_SPECIFICATION.format(
                path=location, filename=PERIODICWEEKLYFILE
            )
        )
        self.checkpoints_month_file = self._read_file(
            PATH_SPECIFICATION.format(
                path=location, filename=CHECKPOINTSMONTHFILE
            )
        )
        self.periodic_month_file = self._read_file(
            PATH_SPECIFICATION.format(
                path=location, filename=PERIODICMONTHLYFILE
            )
        )
        self.checkpoints_quarter_file = self._read_file(
            PATH_SPECIFICATION.format(
                path=location, filename=CHECKPOINTSQUARTERFILE
            )
        )
        self.periodic_quarter_file = self._read_file(
            PATH_SPECIFICATION.format(
                path=location, filename=PERIODICQUARTERLYFILE
            )
        )
        self.checkpoints_year_file = self._read_file(
            PATH_SPECIFICATION.format(
                path=location, filename=CHECKPOINTSYEARFILE
            )
        )
        self.periodic_year_file = self._read_file(
            PATH_SPECIFICATION.format(
                path=location, filename=PERIODICYEARLYFILE
            )
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
        """ Look at the SCHEDULED section of the tasklist and retrive any tasks
        that are due/overdue for the given day (e.g. tomorrow, if preparing
        tomorrow's agenda).

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

    def _log_filename(self, period):
        """ A time period uniquely maps to a single log file on disk for a
        particular planner instance (which is tied to a wiki root path).  This
        function returns that filename, given a time period.
        """
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
        path = os.path.realpath(
            PATH_SPECIFICATION.format(path=self.location, filename=filename)
        )

        return path

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

    def _write_log_to_file(self, period):
        """ Write the log for the given period to the filesystem.
        If this represents an advancement of the period in question,
        then also update the 'current' state of the planner on disk
        by updating the relevant symbolic link.
        """
        log_attr = self._logfile_attribute(period)
        log = getattr(self, log_attr)
        filename = self._log_filename(period)
        if os.path.isfile(filename):
            is_new = False
        else:
            is_new = True

        # write the file to disk
        self._write_file(log, filename)

        if is_new:
            # update "current" link on disk to the newly created file
            link_name = self._link_name(period)
            filelinkfn = PATH_SPECIFICATION.format(
                path=self.location, filename=link_name
            )
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

    def advance(self, now=None, simulate=False):
        """ Advance planner state to next day, updating week and month info
        as necessary. 'now' arg used only for testing
        """
        # use a bunch of StringIO buffers for the Planner object
        # populate them here from real files
        # after the advance() returns, the handles will be updated to the
        # (possibly new) buffers
        # save to the known files here

        # if successful, the date (self.date) is advanced to the next day
        status = super(FilesystemPlanner, self).advance(now, simulate)

        # check for possible errors in planner state before making any changes
        self._check_files_for_contained_periods(status)

        # if this is a simulation, we're good to go - let's break out
        # of the matrix
        if status >= Day:
            if simulate:
                raise SimulationPassedError("All systems GO", status)
            else:
                # make the changes on disk
                self.save(status)

        return status

    def check_log_completion(self, period):
        """ Check the logfile's NOTES section as a determination of whether
        the log has been completed """
        log_attr = self._logfile_attribute(period)
        log = getattr(self, log_attr)
        completed = False
        try:
            notes, _ = read_section(log, 'notes')
        except ValueError:
            raise LogfileLayoutError(
                "Error: No 'NOTES' section found in your log file!"
            )
        notes = notes.read()
        if notes.strip("\n ") != "":
            completed = True
        return completed

    def get_agenda(self, period):
        """ Go through logfile and extract all tasks under AGENDA """
        log_attr = self._logfile_attribute(period)
        log = getattr(self, log_attr)
        try:
            agenda, _ = read_section(log, 'agenda')
        except ValueError:
            raise LogfileLayoutError(
                "No AGENDA section found in today's log file!"
                " Add one and try again."
            )
        agenda = agenda.read()
        return agenda

    def update_agenda(self, period, agenda):
        """ Update the agenda for the given period with the provided agenda by
        appending the new contents to the existing ones.
        """
        log_attr = self._logfile_attribute(period)
        log = getattr(self, log_attr)
        try:
            logfile_updated = add_to_section(
                log, 'agenda', agenda, above=False, ensure_separator=True
            )
        except ValueError:
            raise LogfileLayoutError(
                "No AGENDA section found in today's log file!"
                " Add one and try again."
            )
        setattr(self, log_attr, logfile_updated)

    def _write_files_for_contained_periods(self, period):
        if period == Zero:
            return
        self._write_log_to_file(period)
        self._write_files_for_contained_periods(
            get_next_period(period, decreasing=True)
        )

    def save(self, period=Year):
        """ Write the planner object to the filesystem."""
        # TODO: use pathspec / realpath everywhere.
        # make construct() use pathspec
        # construct full os-specific paths in a single helper
        # with a flag to dereference links (realpath vs abspath probably)
        # reduce redundancy in construct()
        # This completes the R/W flow I think... except for the
        # calling of save in whatsnext which should be moved

        # write the logfiles for the current period as well as
        # all contained periods, since they all advance by one
        self._write_files_for_contained_periods(period)

        if period < Year:
            # write the logfile for the encompassing period
            next_period = get_next_period(period)
            self._write_log_to_file(next_period)
        tasklist_filename = os.path.realpath(
            PATH_SPECIFICATION.format(
                path=self.location, filename=PLANNERTASKLISTFILE
            )
        )

        self._write_file(self.tasklistfile, tasklist_filename)

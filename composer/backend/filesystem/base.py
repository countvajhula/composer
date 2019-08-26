import os

from datetime import datetime

from ... import config
from ..base import PlannerBase
from ...timeperiod import (
    Day,
    Week,
    Month,
    Quarter,
    Year,
    Zero,
    PeriodAdvanceCriteria,
    get_next_day,
)
from . import scheduling
from . import templates
from ...errors import (
    DayStillInProgressError,
    LogfileNotCompletedError,
    PlannerIsInTheFutureError,
    LogfileAlreadyExistsError,
    LogfileLayoutError,
    SimulationPassedError
)
from .utils import add_to_section, quarter_for_month, read_file, write_file, read_section


try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


SCHEDULE_FILE_PREFIX = "Checkpoints"
PLANNERTASKLISTFILE = "TaskList.wiki"
PLANNERDAYTHEMESFILELINK = "DayThemes.wiki"
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


def _next_period(current_period):
    periods = (Zero, Day, Week, Month, Quarter, Year)
    try:
        index = periods.index(current_period)
        next_period = periods[index + 1]
    except (IndexError, ValueError):
        raise
    return next_period


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
        plannerdatelink = "{}/{}".format(self.location, PLANNERDAYFILELINK)
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
            "{}/{}".format(location, PLANNERTASKLISTFILE)
        )
        self.daythemesfile = self._read_file(
            "{}/{}".format(location, PLANNERDAYTHEMESFILELINK)
        )
        self.dayfile = self._read_file(
            "{}/{}".format(location, PLANNERDAYFILELINK)
        )
        self.weekfile = self._read_file(
            "{}/{}".format(location, PLANNERWEEKFILELINK)
        )
        self.monthfile = self._read_file(
            "{}/{}".format(location, PLANNERMONTHFILELINK)
        )
        self.quarterfile = self._read_file(
            "{}/{}".format(location, PLANNERQUARTERFILELINK)
        )
        self.yearfile = self._read_file(
            "{}/{}".format(location, PLANNERYEARFILELINK)
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
            "{}/{}".format(location, PERIODICDAILYFILE)
        )
        self.checkpoints_week_file = self._read_file(
            "{}/{}".format(location, CHECKPOINTSWEEKFILE)
        )
        self.periodic_week_file = self._read_file(
            "{}/{}".format(location, PERIODICWEEKLYFILE)
        )
        self.checkpoints_month_file = self._read_file(
            "{}/{}".format(location, CHECKPOINTSMONTHFILE)
        )
        self.periodic_month_file = self._read_file(
            "{}/{}".format(location, PERIODICMONTHLYFILE)
        )
        self.checkpoints_quarter_file = self._read_file(
            "{}/{}".format(location, CHECKPOINTSQUARTERFILE)
        )
        self.periodic_quarter_file = self._read_file(
            "{}/{}".format(location, PERIODICQUARTERLYFILE)
        )
        self.checkpoints_year_file = self._read_file(
            "{}/{}".format(location, CHECKPOINTSYEARFILE)
        )
        self.periodic_year_file = self._read_file(
            "{}/{}".format(location, PERIODICYEARLYFILE)
        )

    def _write_new_logfile(self, logfile, link_name, new_filename):
        # extract new period filename from date
        # write buffer to new file
        # update currentyear symlink
        self._write_file(logfile, new_filename)
        filelinkfn = "{}/{}".format(self.location, link_name)
        if os.path.islink(filelinkfn):
            os.remove(filelinkfn)
        os.symlink(
            new_filename[new_filename.rfind("/") + 1 :], filelinkfn
        )  # remove path from filename so it isn't "double counted"

    def _update_existing_logfile(self, logfile, filename):
        # write buffer to existing file
        self._write_file(logfile, filename)

    def advance_period(self, current_period=None):
        """ Recursive function to advance planner by day, week, month, quarter, or year
        as the case may be.
        """
        if not current_period:
            current_period = Zero
        next_day = get_next_day(self.date)  # the new day to advance to
        next_period = _next_period(current_period)
        period_criteria_met = next_period.advance_criteria_met(self, self.now)
        if period_criteria_met == PeriodAdvanceCriteria.Satisfied:
            current_period = next_period
            logfile = current_period.get_logfile(self)
            if self.logfile_completion_checking == config.LOGFILE_CHECKING[
                "STRICT"
            ] and not self.check_log_completion(logfile):
                periodstr = current_period.get_name()
                msg = (
                    "Looks like you haven't completed your %s's log."
                    " Would you like to do that now?" % periodstr
                )
                raise LogfileNotCompletedError(msg, periodstr)
            templates.write_new_template(self, current_period, next_day)

            if current_period < Year:
                return self.advance_period(current_period)
        elif period_criteria_met == PeriodAdvanceCriteria.DayStillInProgress:
            raise DayStillInProgressError(
                "Current day is still in progress! Update after 6pm"
            )
        elif period_criteria_met == PeriodAdvanceCriteria.PlannerInFuture:
            raise PlannerIsInTheFutureError("Planner is in the future!")
        else:
            templates.write_existing_template(self, next_period, next_day)
        return current_period

    def advance(self, now=None, simulate=False):
        """ Advance planner state to next day, updating week and month info
        as necessary. 'now' arg used only for testing
        """
        # use a bunch of StringIO buffers for the Planner object
        # populate them here from real files
        # after the advance() returns, the handles will be updated to the
        # (possibly new) buffers
        # save to the known files here

        if not now:
            now = datetime.now()

        self.now = now

        scheduling.schedule_tasks(self)

        status = self.advance_period(Zero)
        if status > Zero:
            self.date = self.next_day

        self.advance_filesystem(status, simulate)
        return status

    def advance_filesystem(self, status, simulate):
        tasklistfn = "{}/{}".format(self.location, PLANNERTASKLISTFILE)
        dayfn_pre = "{}/{}".format(self.location, PLANNERDAYFILELINK)
        dayfn_pre = "{}/{}".format(self.location, os.readlink(dayfn_pre))
        weekfn_pre = "{}/{}".format(self.location, PLANNERWEEKFILELINK)
        weekfn_pre = "{}/{}".format(self.location, os.readlink(weekfn_pre))
        monthfn_pre = "{}/{}".format(self.location, PLANNERMONTHFILELINK)
        monthfn_pre = "{}/{}".format(self.location, os.readlink(monthfn_pre))
        quarterfn_pre = "{}/{}".format(self.location, PLANNERQUARTERFILELINK)
        quarterfn_pre = "{}/{}".format(
            self.location, os.readlink(quarterfn_pre)
        )
        yearfn_pre = "{}/{}".format(self.location, PLANNERYEARFILELINK)
        yearfn_pre = "{}/{}".format(self.location, os.readlink(yearfn_pre))

        next_day = self.date
        (date, month, year) = (
            next_day.day,
            next_day.strftime("%B"),
            next_day.year,
        )
        # check for possible errors in planner state before making any changes
        if status >= Year:
            yearfn_post = "{path}/{year}.wiki".format(
                path=self.location, year=year
            )
            if os.path.isfile(yearfn_post):
                raise LogfileAlreadyExistsError(
                    "New year logfile already exists!"
                )
        if status >= Quarter:
            quarterfn_post = "{path}/{quarter} {year}.wiki".format(
                path=self.location, quarter=quarter_for_month(month), year=year
            )
            if os.path.isfile(quarterfn_post):
                raise LogfileAlreadyExistsError(
                    "New quarter logfile already exists!"
                )
        if status >= Month:
            monthfn_post = "{path}/Month of {month}, {year}.wiki".format(
                path=self.location, month=month, year=year
            )
            if os.path.isfile(monthfn_post):
                raise LogfileAlreadyExistsError(
                    "New month logfile already exists!"
                )
        if status >= Week:
            weekfn_post = "{path}/Week of {month} {date}, {year}.wiki".format(
                path=self.location, month=month, date=date, year=year
            )
            if os.path.isfile(weekfn_post):
                raise LogfileAlreadyExistsError(
                    "New week logfile already exists!"
                )
        if status >= Day:
            dayfn_post = "{path}/{month} {date}, {year}.wiki".format(
                path=self.location, month=month, date=date, year=year
            )
            if os.path.isfile(dayfn_post):
                raise LogfileAlreadyExistsError(
                    "New day logfile already exists!"
                )

        # if this is a simulation, we're good to go - let's break out
        # of the matrix
        if status >= Day and simulate:
            raise SimulationPassedError("All systems GO", status)

        # make the changes on disk
        if status >= Year:
            self._write_new_logfile(
                self.yearfile, PLANNERYEARFILELINK, yearfn_post
            )
        if status >= Quarter:
            self._write_new_logfile(
                self.quarterfile, PLANNERQUARTERFILELINK, quarterfn_post
            )
        if status == Quarter:
            self._update_existing_logfile(self.yearfile, yearfn_pre)
        if status >= Month:
            self._write_new_logfile(
                self.monthfile, PLANNERMONTHFILELINK, monthfn_post
            )
        if status == Month:
            self._update_existing_logfile(self.quarterfile, quarterfn_pre)
        if status >= Week:
            self._write_new_logfile(
                self.weekfile, PLANNERWEEKFILELINK, weekfn_post
            )
        if status == Week:
            self._update_existing_logfile(self.monthfile, monthfn_pre)
        if status >= Day:
            self._write_new_logfile(
                self.dayfile, PLANNERDAYFILELINK, dayfn_post
            )
            # in any event if day was advanced, update tasklist
            self._update_existing_logfile(self.tasklistfile, tasklistfn)
        if status == Day:
            self._update_existing_logfile(self.weekfile, weekfn_pre)

    def check_log_completion(self, log):
        """ Check the logfile's NOTES section as a determination of whether
        the log has been completed """
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

    def get_agenda(self, log):
        """ Go through logfile and extract all tasks under AGENDA """
        try:
            agenda, _ = read_section(log, 'agenda')
        except ValueError:
            raise LogfileLayoutError(
                "No AGENDA section found in today's log file!"
                " Add one and try again."
            )
        agenda = agenda.read()
        agenda = agenda.strip("\n")  # TODO: remove
        return agenda

    def update_agenda(self, log, agenda):
        """ Append the provided agenda to the agenda contained in the logfile,
        and return the updated logfile (without mutating the original).
        """
        # TODO: should probably go through a setter to mutate here instead
        try:
            logfile_updated = add_to_section(
                log, 'agenda', agenda, above=False, ensure_separator=True
            )
        except ValueError:
            raise LogfileLayoutError(
                "No AGENDA section found in today's log file!"
                " Add one and try again."
            )
        return logfile_updated

    def save(self):
        """ Write the planner object to the filesystem at the given path."""
        pathspec = "{}/{}"
        tasklist_filename = pathspec.format(self.location, PLANNERTASKLISTFILE)
        day_filename = os.path.realpath(
            pathspec.format(self.location, PLANNERDAYFILELINK)
        )
        week_filename = os.path.realpath(
            pathspec.format(self.location, PLANNERWEEKFILELINK)
        )
        month_filename = os.path.realpath(
            pathspec.format(self.location, PLANNERMONTHFILELINK)
        )
        quarter_filename = os.path.realpath(
            pathspec.format(self.location, PLANNERQUARTERFILELINK)
        )
        year_filename = os.path.realpath(
            pathspec.format(self.location, PLANNERYEARFILELINK)
        )

        self._write_file(self.tasklistfile, tasklist_filename)
        self._write_file(self.yearfile, year_filename)
        self._write_file(self.quarterfile, quarter_filename)
        self._write_file(self.monthfile, month_filename)
        self._write_file(self.weekfile, week_filename)
        self._write_file(self.dayfile, day_filename)

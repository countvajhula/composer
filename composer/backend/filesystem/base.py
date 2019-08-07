import os

from datetime import datetime

from . import advanceplanner
from ..base import PlannerBase
from ... import config
from ... import scheduling
from ... import utils
from ...errors import (
    PlannerStateError,
    SimulationPassedError)


try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


SCHEDULE_FILE_PREFIX = 'Checkpoints'
PLANNERTASKLISTFILE = 'TaskList.wiki'
PLANNERDAYTHEMESFILELINK = 'DayThemes.wiki'
PLANNERDAYFILELINK = 'currentday'
PLANNERWEEKFILELINK = 'currentweek'
PLANNERMONTHFILELINK = 'currentmonth'
PLANNERQUARTERFILELINK = 'currentquarter'
PLANNERYEARFILELINK = 'currentyear'
CHECKPOINTSWEEKFILE = 'Checkpoints_Week.wiki'
CHECKPOINTSMONTHFILE = 'Checkpoints_Month.wiki'
CHECKPOINTSQUARTERFILE = 'Checkpoints_Quarter.wiki'
CHECKPOINTSYEARFILE = 'Checkpoints_Year.wiki'
PERIODICYEARLYFILE = 'Periodic_Yearly.wiki'
PERIODICQUARTERLYFILE = 'Periodic_Quarterly.wiki'
PERIODICMONTHLYFILE = 'Periodic_Monthly.wiki'
PERIODICWEEKLYFILE = 'Periodic_Weekly.wiki'
PERIODICDAILYFILE = 'Periodic_Daily.wiki'


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
        with open(filename, 'r') as f:
            result = StringIO(f.read())
        return result

    def _write_file(self, file, filename):
        # TODO: remove
        utils.write_file(file.read(), filename)
        file.seek(0)

    def _get_date(self):
        """ get planner date, currently looks for the file 'currentday', if dne throw exception """
        plannerdatelink = '{}/{}'.format(self.location, PLANNERDAYFILELINK)
        plannerdatefn = os.readlink(plannerdatelink)
        pathidx = plannerdatefn.rfind('/')
        datestr = plannerdatefn[pathidx + 1:-5]  # trim path from beginning and '.wiki' from end
        plannerdate = datetime.strptime(datestr, '%B %d, %Y').date()
        return plannerdate

    def construct(self, location=None):
        """ Construct a planner object from a filesystem representation."""
        # CURRENT planner date used here
        if location is None:
            # needed for tests atm -- eventually make location a required arg
            return
        self.location = location
        self.date = self._get_date()
        self.tasklistfile = self._read_file('{}/{}'.format(location, PLANNERTASKLISTFILE))
        self.daythemesfile = self._read_file('{}/{}'.format(location, PLANNERDAYTHEMESFILELINK))
        self.dayfile = self._read_file('{}/{}'.format(location, PLANNERDAYFILELINK))
        self.weekfile = self._read_file('{}/{}'.format(location, PLANNERWEEKFILELINK))
        self.monthfile = self._read_file('{}/{}'.format(location, PLANNERMONTHFILELINK))
        self.quarterfile = self._read_file('{}/{}'.format(location, PLANNERQUARTERFILELINK))
        self.yearfile = self._read_file('{}/{}'.format(location, PLANNERYEARFILELINK))

        # daily, weekly, monthly checkpoints, periodic items
        self.checkpoints_weekday_file = self._read_file(
            '{}/{}_Weekday_{}.wiki'
            .format(location,
                    SCHEDULE_FILE_PREFIX,
                    config.PlannerConfig.Schedule.capitalize()))
        self.checkpoints_weekend_file = self._read_file(
            '{}/{}_Weekend_{}.wiki'
            .format(location,
                    SCHEDULE_FILE_PREFIX,
                    config.PlannerConfig.Schedule.capitalize()))
        self.periodic_day_file = self._read_file('{}/{}'.format(location, PERIODICDAILYFILE))
        self.checkpoints_week_file = self._read_file('{}/{}'.format(location, CHECKPOINTSWEEKFILE))
        self.periodic_week_file = self._read_file('{}/{}'.format(location, PERIODICWEEKLYFILE))
        self.checkpoints_month_file = self._read_file('{}/{}'.format(location, CHECKPOINTSMONTHFILE))
        self.periodic_month_file = self._read_file('{}/{}'.format(location, PERIODICMONTHLYFILE))
        self.checkpoints_quarter_file = self._read_file('{}/{}'.format(location, CHECKPOINTSQUARTERFILE))
        self.periodic_quarter_file = self._read_file('{}/{}'.format(location, PERIODICQUARTERLYFILE))
        self.checkpoints_year_file = self._read_file('{}/{}'.format(location, CHECKPOINTSYEARFILE))
        self.periodic_year_file = self._read_file('{}/{}'.format(location, PERIODICYEARLYFILE))

    def advance(self, now=None, simulate=False):
        # use a bunch of StringIO buffers for the Planner object
        # populate them here from real files
        # after the advance() returns, the handles will be updated to the (possibly new) buffers
        # save to the known files here

        status = scheduling.schedule_tasks(self, now)
        status = advanceplanner.advance_planner(self, now)

        tasklistfn = '{}/{}'.format(self.location, PLANNERTASKLISTFILE)
        dayfn_pre = '{}/{}'.format(self.location, PLANNERDAYFILELINK)
        dayfn_pre = '{}/{}'.format(self.location, os.readlink(dayfn_pre))
        weekfn_pre = '{}/{}'.format(self.location, PLANNERWEEKFILELINK)
        weekfn_pre = '{}/{}'.format(self.location, os.readlink(weekfn_pre))
        monthfn_pre = '{}/{}'.format(self.location, PLANNERMONTHFILELINK)
        monthfn_pre = '{}/{}'.format(self.location, os.readlink(monthfn_pre))
        quarterfn_pre = '{}/{}'.format(self.location, PLANNERQUARTERFILELINK)
        quarterfn_pre = '{}/{}'.format(self.location, os.readlink(quarterfn_pre))
        yearfn_pre = '{}/{}'.format(self.location, PLANNERYEARFILELINK)
        yearfn_pre = '{}/{}'.format(self.location, os.readlink(yearfn_pre))

        next_day = self.date
        (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
        # check for possible errors in planner state before making any changes
        if status >= utils.PlannerPeriod.Year:
            yearfn_post = '{path}/{year}.wiki'.format(path=self.location, year=year)
            if os.path.isfile(yearfn_post): raise PlannerStateError("New year logfile already exists!")
        if status >= utils.PlannerPeriod.Quarter:
            quarterfn_post = '{path}/{quarter} {year}.wiki'.format(path=self.location, quarter=utils.quarter_for_month(month), year=year)
            if os.path.isfile(quarterfn_post): raise PlannerStateError("New quarter logfile already exists!")
        if status >= utils.PlannerPeriod.Month:
            monthfn_post = '{path}/Month of {month}, {year}.wiki'.format(path=self.location, month=month, year=year)
            if os.path.isfile(monthfn_post): raise PlannerStateError("New month logfile already exists!")
        if status >= utils.PlannerPeriod.Week:
            weekfn_post = '{path}/Week of {month} {date}, {year}.wiki'.format(path=self.location, month=month, date=date, year=year)
            if os.path.isfile(weekfn_post): raise PlannerStateError("New week logfile already exists!")
        if status >= utils.PlannerPeriod.Day:
            dayfn_post = '{path}/{month} {date}, {year}.wiki'.format(path=self.location, month=month, date=date, year=year)
            if os.path.isfile(dayfn_post): raise PlannerStateError("New day logfile already exists!")

        # if this is a simulation, we're good to go - let's break out of the matrix
        if status >= utils.PlannerPeriod.Day and simulate:
            raise SimulationPassedError('All systems GO', status)

        if status >= utils.PlannerPeriod.Year:
            # extract new year filename from date
            # write buffer to new file
            # update currentyear symlink
            self._write_file(self.yearfile, yearfn_post)
            filelinkfn = '{}/{}'.format(self.location, PLANNERYEARFILELINK)
            if os.path.islink(filelinkfn):
                os.remove(filelinkfn)
            os.symlink(yearfn_post[yearfn_post.rfind('/') + 1:], filelinkfn)  # remove path from filename so it isn't "double counted"
        if status >= utils.PlannerPeriod.Quarter:
            # extract new quarter filename from date
            # write buffer to new file
            # update currentquarter symlink
            self._write_file(self.quarterfile, quarterfn_post)
            filelinkfn = '{}/{}'.format(self.location, PLANNERQUARTERFILELINK)
            if os.path.islink(filelinkfn):
                os.remove(filelinkfn)
            os.symlink(quarterfn_post[quarterfn_post.rfind('/') + 1:], filelinkfn) # remove path from filename so it isn't "double counted"
        if status == utils.PlannerPeriod.Quarter:
            # write year buffer to existing file
            self._write_file(self.yearfile, yearfn_pre)
        if status >= utils.PlannerPeriod.Month:
            # extract new month filename from date
            # write buffer to new file
            # update currentmonth symlink
            self._write_file(self.monthfile, monthfn_post)
            filelinkfn = '{}/{}'.format(self.location, PLANNERMONTHFILELINK)
            if os.path.islink(filelinkfn):
                os.remove(filelinkfn)
            os.symlink(monthfn_post[monthfn_post.rfind('/') + 1:], filelinkfn)  # remove path from filename so it isn't "double counted"
        if status == utils.PlannerPeriod.Month:
            # write quarter buffer to existing file
            self._write_file(self.quarterfile, quarterfn_pre)
        if status >= utils.PlannerPeriod.Week:
            # extract new week filename from date
            # write buffer to new file
            # update currentweek symlink
            self._write_file(self.weekfile, weekfn_post)
            filelinkfn = '{}/{}'.format(self.location, PLANNERWEEKFILELINK)
            if os.path.islink(filelinkfn):
                os.remove(filelinkfn)
            os.symlink(weekfn_post[weekfn_post.rfind('/') + 1:], filelinkfn)  # remove path from filename so it isn't "double counted"
        if status == utils.PlannerPeriod.Week:
            # write month buffer to existing file
            self._write_file(self.monthfile, monthfn_pre)
        if status >= utils.PlannerPeriod.Day:
            # extract new day filename from date
            # write buffer to new file
            # update currentday symlink
            self._write_file(self.dayfile, dayfn_post)
            filelinkfn = '{}/{}'.format(self.location, PLANNERDAYFILELINK)
            if os.path.islink(filelinkfn):
                os.remove(filelinkfn)
            os.symlink(dayfn_post[dayfn_post.rfind('/') + 1:], filelinkfn)  # remove path from filename so it isn't "double counted"
            # in any event if day was advanced, update tasklist
            self._write_file(self.tasklistfile, tasklistfn)
        if status == utils.PlannerPeriod.Day:
            # write week buffer to existing file
            self._write_file(self.weekfile, weekfn_pre)

        return status

    def get_agenda(self, log):
        advanceplanner.extract_agenda_from_logfile(log)

    def update_agenda(self, log, agenda):
        """ Append the provided agenda to the agenda contained in the logfile,
        and return the updated logfile (without mutating the original).
        """
        # TODO: should probably go through a setter to mutate here instead
        return advanceplanner.update_logfile_agenda(log, agenda)

    def reset_heads_on_files(self):
        # TODO: define relevant atomic operations so that this isn't necessary
        self.tasklistfile.seek(0)
        self.daythemesfile.seek(0)
        self.dayfile.seek(0)
        self.weekfile.seek(0)
        self.monthfile.seek(0)
        self.quarterfile.seek(0)
        self.yearfile.seek(0)
        self.checkpoints_year_file.seek(0)
        self.periodic_year_file.seek(0)
        self.checkpoints_quarter_file.seek(0)
        self.periodic_quarter_file.seek(0)
        self.checkpoints_month_file.seek(0)
        self.periodic_month_file.seek(0)
        self.checkpoints_week_file.seek(0)
        self.periodic_week_file.seek(0)
        self.checkpoints_weekday_file.seek(0)
        self.checkpoints_weekend_file.seek(0)
        self.periodic_day_file.seek(0)

    def save(self):
        """ Write the planner object to the filesystem at the given path."""
        pathspec = '{}/{}'
        tasklist_filename = pathspec.format(self.location, PLANNERTASKLISTFILE)
        day_filename = os.path.realpath(pathspec.format(self.location, PLANNERDAYFILELINK))
        week_filename = os.path.realpath(pathspec.format(self.location, PLANNERWEEKFILELINK))
        month_filename = os.path.realpath(pathspec.format(self.location, PLANNERMONTHFILELINK))
        quarter_filename = os.path.realpath(pathspec.format(self.location, PLANNERQUARTERFILELINK))
        year_filename = os.path.realpath(pathspec.format(self.location, PLANNERYEARFILELINK))

        self._write_file(self.tasklistfile, tasklist_filename)
        self._write_file(self.yearfile, year_filename)
        self._write_file(self.quarterfile, quarter_filename)
        self._write_file(self.monthfile, month_filename)
        self._write_file(self.weekfile, week_filename)
        self._write_file(self.dayfile, day_filename)

        self.reset_heads_on_files()

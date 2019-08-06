import os

from datetime import datetime

from .base import PlannerBase
from .. import advanceplanner
from .. import config
from .. import scheduling
from .. import utils
from ..errors import (
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
    tasklistfile = None
    daythemesfile = None
    dayfile = None
    weekfile = None
    monthfile = None
    quarterfile = None
    yearfile = None
    checkpoints_weekday_file = None
    checkpoints_weekend_file = None
    checkpoints_week_file = None
    checkpoints_month_file = None
    checkpoints_quarter_file = None
    checkpoints_year_file = None
    periodic_day_file = None
    periodic_week_file = None
    periodic_month_file = None
    periodic_quarter_file = None
    periodic_year_file = None

    def __init__(self, location=None):
        self.construct(location)

    def _read_file(self, filename):
        """ Read a file on disk and produce an in-memory logical representation
        of the file. This logical representation will be used for analysis and
        processing so that the actual file on disk isn't affected until any
        such processing is complete.
        """
        with open(filename, 'r') as f:
            result = StringIO(f.read())
        return result

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
            utils.write_file(self.yearfile.read(), yearfn_post)
            filelinkfn = '{}/{}'.format(self.location, PLANNERYEARFILELINK)
            if os.path.islink(filelinkfn):
                os.remove(filelinkfn)
            os.symlink(yearfn_post[yearfn_post.rfind('/') + 1:], filelinkfn)  # remove path from filename so it isn't "double counted"
        if status >= utils.PlannerPeriod.Quarter:
            # extract new quarter filename from date
            # write buffer to new file
            # update currentquarter symlink
            utils.write_file(self.quarterfile.read(), quarterfn_post)
            filelinkfn = '{}/{}'.format(self.location, PLANNERQUARTERFILELINK)
            if os.path.islink(filelinkfn):
                os.remove(filelinkfn)
            os.symlink(quarterfn_post[quarterfn_post.rfind('/') + 1:], filelinkfn) # remove path from filename so it isn't "double counted"
        if status == utils.PlannerPeriod.Quarter:
            # write year buffer to existing file
            utils.write_file(self.yearfile.read(), yearfn_pre)
        if status >= utils.PlannerPeriod.Month:
            # extract new month filename from date
            # write buffer to new file
            # update currentmonth symlink
            utils.write_file(self.monthfile.read(), monthfn_post)
            filelinkfn = '{}/{}'.format(self.location, PLANNERMONTHFILELINK)
            if os.path.islink(filelinkfn):
                os.remove(filelinkfn)
            os.symlink(monthfn_post[monthfn_post.rfind('/') + 1:], filelinkfn)  # remove path from filename so it isn't "double counted"
        if status == utils.PlannerPeriod.Month:
            # write quarter buffer to existing file
            utils.write_file(self.quarterfile.read(), quarterfn_pre)
        if status >= utils.PlannerPeriod.Week:
            # extract new week filename from date
            # write buffer to new file
            # update currentweek symlink
            utils.write_file(self.weekfile.read(), weekfn_post)
            filelinkfn = '{}/{}'.format(self.location, PLANNERWEEKFILELINK)
            if os.path.islink(filelinkfn):
                os.remove(filelinkfn)
            os.symlink(weekfn_post[weekfn_post.rfind('/') + 1:], filelinkfn)  # remove path from filename so it isn't "double counted"
        if status == utils.PlannerPeriod.Week:
            # write month buffer to existing file
            utils.write_file(self.monthfile.read(), monthfn_pre)
        if status >= utils.PlannerPeriod.Day:
            # extract new day filename from date
            # write buffer to new file
            # update currentday symlink
            utils.write_file(self.dayfile.read(), dayfn_post)
            filelinkfn = '{}/{}'.format(self.location, PLANNERDAYFILELINK)
            if os.path.islink(filelinkfn):
                os.remove(filelinkfn)
            os.symlink(dayfn_post[dayfn_post.rfind('/') + 1:], filelinkfn)  # remove path from filename so it isn't "double counted"
            # in any event if day was advanced, update tasklist
            utils.write_file(self.tasklistfile.read(), tasklistfn)
        if status == utils.PlannerPeriod.Day:
            # write week buffer to existing file
            utils.write_file(self.weekfile.read(), weekfn_pre)

        return status

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

        utils.write_file(self.tasklistfile.read(), tasklist_filename)
        utils.write_file(self.yearfile.read(), year_filename)
        utils.write_file(self.quarterfile.read(), quarter_filename)
        utils.write_file(self.monthfile.read(), month_filename)
        utils.write_file(self.weekfile.read(), week_filename)
        utils.write_file(self.dayfile.read(), day_filename)

        self.reset_heads_on_files()

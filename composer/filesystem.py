import datetime
import os

from . import config
from . import utils
from . import scheduling
from . import advanceplanner
from .backend.filesystem import FilesystemPlanner
from .errors import (
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


def get_planner_date_from_string(datestr):
    return datetime.datetime.strptime(datestr, '%B %d, %Y').date()


def get_planner_date(plannerlocation):
    """ get planner date, currently looks for the file 'currentday', if dne throw exception """
    plannerdatelink = '%s/%s' % (plannerlocation, PLANNERDAYFILELINK)
    plannerdatefn = os.readlink(plannerdatelink)
    pathidx = plannerdatefn.rfind('/')
    datestr = plannerdatefn[pathidx + 1:-5]  # trim path from beginning and '.wiki' from end
    plannerdate = get_planner_date_from_string(datestr)
    return plannerdate


def _read_file(filename):
    with open(filename, 'r') as f:
        result = StringIO(f.read())
    return result


def construct_planner_from_filesystem(plannerpath):
    """ Construct a planner object from a filesystem representation."""
    # CURRENT planner date used here
    planner = FilesystemPlanner()
    planner.date = get_planner_date(plannerpath)
    planner.tasklistfile = _read_file('{}/{}'.format(plannerpath, PLANNERTASKLISTFILE))
    planner.daythemesfile = _read_file('{}/{}'.format(plannerpath, PLANNERDAYTHEMESFILELINK))
    planner.dayfile = _read_file('{}/{}'.format(plannerpath, PLANNERDAYFILELINK))
    planner.weekfile = _read_file('{}/{}'.format(plannerpath, PLANNERWEEKFILELINK))
    planner.monthfile = _read_file('{}/{}'.format(plannerpath, PLANNERMONTHFILELINK))
    planner.quarterfile = _read_file('{}/{}'.format(plannerpath, PLANNERQUARTERFILELINK))
    planner.yearfile = _read_file('{}/{}'.format(plannerpath, PLANNERYEARFILELINK))

    # daily, weekly, monthly checkpoints, periodic items
    planner.checkpoints_weekday_file = _read_file(
        '{}/{}_Weekday_{}.wiki'
        .format(plannerpath,
                SCHEDULE_FILE_PREFIX,
                config.PlannerConfig.Schedule.capitalize()))
    planner.checkpoints_weekend_file = _read_file(
        '{}/{}_Weekend_{}.wiki'
        .format(plannerpath,
                SCHEDULE_FILE_PREFIX,
                config.PlannerConfig.Schedule.capitalize()))
    planner.periodic_day_file = _read_file('{}/{}'.format(plannerpath, PERIODICDAILYFILE))
    planner.checkpoints_week_file = _read_file('{}/{}'.format(plannerpath, CHECKPOINTSWEEKFILE))
    planner.periodic_week_file = _read_file('{}/{}'.format(plannerpath, PERIODICWEEKLYFILE))
    planner.checkpoints_month_file = _read_file('{}/{}'.format(plannerpath, CHECKPOINTSMONTHFILE))
    planner.periodic_month_file = _read_file('{}/{}'.format(plannerpath, PERIODICMONTHLYFILE))
    planner.checkpoints_quarter_file = _read_file('{}/{}'.format(plannerpath, CHECKPOINTSQUARTERFILE))
    planner.periodic_quarter_file = _read_file('{}/{}'.format(plannerpath, PERIODICQUARTERLYFILE))
    planner.checkpoints_year_file = _read_file('{}/{}'.format(plannerpath, CHECKPOINTSYEARFILE))
    planner.periodic_year_file = _read_file('{}/{}'.format(plannerpath, PERIODICYEARLYFILE))

    return planner


def _write_file(contents, filename):
    with open(filename, 'w') as f:
        f.write(contents)


def write_planner_to_filesystem(planner, plannerpath):
    """ Write the planner object to the filesystem at the given path."""
    pathspec = '{}/{}'
    tasklist_filename = pathspec.format(plannerpath, PLANNERTASKLISTFILE)
    day_filename = os.path.realpath(pathspec.format(plannerpath, PLANNERDAYFILELINK))
    week_filename = os.path.realpath(pathspec.format(plannerpath, PLANNERWEEKFILELINK))
    month_filename = os.path.realpath(pathspec.format(plannerpath, PLANNERMONTHFILELINK))
    quarter_filename = os.path.realpath(pathspec.format(plannerpath, PLANNERQUARTERFILELINK))
    year_filename = os.path.realpath(pathspec.format(plannerpath, PLANNERYEARFILELINK))

    _write_file(planner.tasklistfile.read(), tasklist_filename)
    _write_file(planner.yearfile.read(), year_filename)
    _write_file(planner.quarterfile.read(), quarter_filename)
    _write_file(planner.monthfile.read(), month_filename)
    _write_file(planner.weekfile.read(), week_filename)
    _write_file(planner.dayfile.read(), day_filename)

    utils.reset_heads_on_planner_files(planner)


def advance_filesystem_planner(plannerpath, now=None, simulate=False):
    # use a bunch of StringIO buffers for the Planner object
    # populate them here from real files
    # after the advance() returns, the handles will be updated to the (possibly new) buffers
    # save to the known files here

    planner = construct_planner_from_filesystem(plannerpath)

    status = scheduling.schedule_tasks(planner, now)
    status = advanceplanner.advance_planner(planner, now)

    tasklistfn = '%s/%s' % (plannerpath, PLANNERTASKLISTFILE)
    dayfn_pre = '%s/%s' % (plannerpath, PLANNERDAYFILELINK)
    dayfn_pre = '%s/%s' % (plannerpath, os.readlink(dayfn_pre))
    weekfn_pre = '%s/%s' % (plannerpath, PLANNERWEEKFILELINK)
    weekfn_pre = '%s/%s' % (plannerpath, os.readlink(weekfn_pre))
    monthfn_pre = '%s/%s' % (plannerpath, PLANNERMONTHFILELINK)
    monthfn_pre = '%s/%s' % (plannerpath, os.readlink(monthfn_pre))
    quarterfn_pre = '%s/%s' % (plannerpath, PLANNERQUARTERFILELINK)
    quarterfn_pre = '%s/%s' % (plannerpath, os.readlink(quarterfn_pre))
    yearfn_pre = '%s/%s' % (plannerpath, PLANNERYEARFILELINK)
    yearfn_pre = '%s/%s' % (plannerpath, os.readlink(yearfn_pre))

    next_day = planner.date
    (date, day, month, year) = (next_day.day, next_day.strftime('%A'), next_day.strftime('%B'), next_day.year)
    # check for possible errors in planner state before making any changes
    if status >= utils.PlannerPeriod.Year:
        yearfn_post = '%s/%d.wiki' % (plannerpath, year)
        if os.path.isfile(yearfn_post): raise PlannerStateError("New year logfile already exists!")
    if status >= utils.PlannerPeriod.Quarter:
        quarterfn_post = '%s/%s %d.wiki' % (plannerpath, utils.quarter_for_month(month), year)
        if os.path.isfile(quarterfn_post): raise PlannerStateError("New quarter logfile already exists!")
    if status >= utils.PlannerPeriod.Month:
        monthfn_post = '%s/Month of %s, %d.wiki' % (plannerpath, month, year)
        if os.path.isfile(monthfn_post): raise PlannerStateError("New month logfile already exists!")
    if status >= utils.PlannerPeriod.Week:
        weekfn_post = '%s/Week of %s %d, %d.wiki' % (plannerpath, month, date, year)
        if os.path.isfile(weekfn_post): raise PlannerStateError("New week logfile already exists!")
    if status >= utils.PlannerPeriod.Day:
        dayfn_post = '%s/%s %d, %d.wiki' % (plannerpath, month, date, year)
        if os.path.isfile(dayfn_post): raise PlannerStateError("New day logfile already exists!")

    # if this is a simulation, we're good to go - let's break out of the matrix
    if status >= utils.PlannerPeriod.Day and simulate:
        raise SimulationPassedError('All systems GO', status)

    if status >= utils.PlannerPeriod.Year:
        # extract new year filename from date
        # write buffer to new file
        # update currentyear symlink
        yearfn_post = '%s/%d.wiki' % (plannerpath, year)
        _write_file(planner.yearfile.read(), yearfn_post)
        filelinkfn = '%s/%s' % (plannerpath, PLANNERYEARFILELINK)
        if os.path.islink(filelinkfn):
            os.remove(filelinkfn)
        os.symlink(yearfn_post[yearfn_post.rfind('/') + 1:], filelinkfn)  # remove path from filename so it isn't "double counted"
    if status >= utils.PlannerPeriod.Quarter:
        # extract new quarter filename from date
        # write buffer to new file
        # update currentquarter symlink
        quarterfn_post = '%s/%s %d.wiki' % (plannerpath, utils.quarter_for_month(month), year)
        _write_file(planner.quarterfile.read(), quarterfn_post)
        filelinkfn = '%s/%s' % (plannerpath, PLANNERQUARTERFILELINK)
        if os.path.islink(filelinkfn):
            os.remove(filelinkfn)
        os.symlink(quarterfn_post[quarterfn_post.rfind('/') + 1:], filelinkfn) # remove path from filename so it isn't "double counted"
    if status == utils.PlannerPeriod.Quarter:
        # write year buffer to existing file
        _write_file(planner.yearfile.read(), yearfn_pre)
    if status >= utils.PlannerPeriod.Month:
        # extract new month filename from date
        # write buffer to new file
        # update currentmonth symlink
        monthfn_post = '%s/Month of %s, %d.wiki' % (plannerpath, month, year)
        _write_file(planner.monthfile.read(), monthfn_post)
        filelinkfn = '%s/%s' % (plannerpath, PLANNERMONTHFILELINK)
        if os.path.islink(filelinkfn):
            os.remove(filelinkfn)
        os.symlink(monthfn_post[monthfn_post.rfind('/') + 1:], filelinkfn)  # remove path from filename so it isn't "double counted"
    if status == utils.PlannerPeriod.Month:
        # write quarter buffer to existing file
        _write_file(planner.quarterfile.read(), quarterfn_pre)
    if status >= utils.PlannerPeriod.Week:
        # extract new week filename from date
        # write buffer to new file
        # update currentweek symlink
        weekfn_post = '%s/Week of %s %d, %d.wiki' % (plannerpath, month, date, year)
        _write_file(planner.weekfile.read(), weekfn_post)
        filelinkfn = '%s/%s' % (plannerpath, PLANNERWEEKFILELINK)
        if os.path.islink(filelinkfn):
            os.remove(filelinkfn)
        os.symlink(weekfn_post[weekfn_post.rfind('/') + 1:], filelinkfn)  # remove path from filename so it isn't "double counted"
    if status == utils.PlannerPeriod.Week:
        # write month buffer to existing file
        _write_file(planner.monthfile.read(), monthfn_pre)
    if status >= utils.PlannerPeriod.Day:
        # extract new day filename from date
        # write buffer to new file
        # update currentday symlink
        dayfn_post = '%s/%s %d, %d.wiki' % (plannerpath, month, date, year)
        _write_file(planner.dayfile.read(), dayfn_post)
        filelinkfn = '%s/%s' % (plannerpath, PLANNERDAYFILELINK)
        if os.path.islink(filelinkfn):
            os.remove(filelinkfn)
        os.symlink(dayfn_post[dayfn_post.rfind('/') + 1:], filelinkfn)  # remove path from filename so it isn't "double counted"
        # in any event if day was advanced, update tasklist
        _write_file(planner.tasklistfile.read(), tasklistfn)
    if status == utils.PlannerPeriod.Day:
        # write week buffer to existing file
        _write_file(planner.weekfile.read(), weekfn_pre)

    return status

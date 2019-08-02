#!/usr/bin/env python

import datetime
import os
import sys
from subprocess import call

import click

from . import advanceplanner
from . import advice
from . import config
from . import filesystem
from . import updateindex
from . import utils

from .errors import (
    BlockedTaskNotScheduledError,
    DateFormatError,
    DayStillInProgressError,
    LogfileLayoutError,
    LogfileNotCompletedError,
    PlannerIsInTheFutureError,
    PlannerStateError,
    SimulationPassedError,
    RelativeDateError,
    TasklistLayoutError,
    TomorrowIsEmptyError)

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO

try:  # py2
    raw_input
except NameError:  # py3
    raw_input = input


CONFIG_FILE = '/Users/siddhartha/work/composer/composer/config.ini'


@click.command(help=('Move on to the next thing in your planning, organizing, '
                     'and tracking workflow.\n'
                     'WIKIPATH is the path of the wiki to operate on.\n'
                     'If not provided, uses the path(s) specified in '
                     'config.ini'))
@click.argument('wikipath', required=False)
@click.option('-t', '--test',
              is_flag=True,
              help=('A temporary flag for testing. To be removed in a future '
                    'version.'))
@click.option('-j', '--jump',
              is_flag=True,
              help='Jump to present day.')
def main(wikipath, test, jump):
    # Moved pending tasks from today over to tomorrow's agenda
    # could try: [Display score for today]

    now = None

    preferences = config.read_user_preferences(CONFIG_FILE)
    # if wikipath is specified, it should override the configured paths in the ini file
    if wikipath:
        wikidirs = [wikipath]
    else:
        wikidirs = preferences['wikis']
    if test:
        # so jump can be tested on test wiki
        now = datetime.datetime(2013, 1, 8, 19, 0, 0)

    if jump:
        print()
        print(">>> Get ready to JUMP! <<<")
        print()

    # simulate the changes first and then when it's all OK, make the necessary
    # preparations (e.g. git commit) and actually perform the changes

    for wikidir in wikidirs:
        simulate = True
        config.set_preferences(preferences, jump)
        print()
        print(">>> Operating on planner at location: %s <<<" % wikidir)
        print()
        while True:
            try:
                filesystem.advance_filesystem_planner(wikidir, now=now, simulate=simulate)
                print()
                print("Moving tasks added for tomorrow over to tomorrow's agenda...")
                print("Carrying over any unfinished tasks from today to tomorrow's agenda...")
                print("Checking for any other tasks previously scheduled for tomorrow...")
                print("Creating/updating log files...")
                print("...DONE.")
                # update index after making changes
                print()
                print("Updating planner wiki index...")
                updateindex.update_index(wikidir)
                print("...DONE.")
                # git commit "after"
                print()
                print("Committing all changes...")
                plannerdate = filesystem.get_planner_date(wikidir)
                (date, month, year) = (plannerdate.day, plannerdate.strftime('%B'), plannerdate.year)
                datestr = '%s %d, %d' % (month, date, year)
                with open(os.devnull, 'w') as null:
                    call(['git', 'add', '-A'], cwd=wikidir, stdout=null)
                    call(['git', 'commit', '-m', 'SOD %s' % datestr], cwd=wikidir, stdout=null)
                print("...DONE.")
                print()
                print("~~~ THOUGHT FOR THE DAY ~~~")
                print()
                filepaths = map(lambda f: wikidir + '/' + f, preferences['lessons_files'])

                def openfile(fn):
                    try:
                        f = open(fn, 'r')
                    except Exception:
                        f = StringIO('')
                    return f
                lessons_files = map(openfile, filepaths)
                print(advice.get_advice(lessons_files))
                if jump:  # if jumping, keep repeating until present-day error thrown
                    simulate = True
                else:
                    break
            except SimulationPassedError as err:
                # print "DEV: simulation passed. let's do this thing ... for real."
                if err.status >= utils.PlannerPeriod.Week:
                    theme = raw_input("(Optional) Enter a theme for the upcoming week, e.g. Week of 'Timeliness', or 'Completion':__")
                    utils.PlannerUserSettings.WeekTheme = theme if theme else None
                if err.status >= utils.PlannerPeriod.Day:
                    # git commit a "before", now that we know changes are about to be written to planner
                    print()
                    print("Saving EOD planner state before making changes...")
                    plannerdate = filesystem.get_planner_date(wikidir)
                    (date, month, year) = (plannerdate.day, plannerdate.strftime('%B'), plannerdate.year)
                    datestr = '%s %d, %d' % (month, date, year)
                    with open(os.devnull, 'w') as null:
                        call(['git', 'add', '-A'], cwd=wikidir, stdout=null)
                        call(['git', 'commit', '-m', 'EOD %s' % datestr], cwd=wikidir, stdout=null)
                    print("...DONE.")
                if err.status >= utils.PlannerPeriod.Day:
                    planner = filesystem.construct_planner_from_filesystem(wikidir)
                    dayagenda = advanceplanner.extract_agenda_from_logfile(planner.dayfile)
                    if dayagenda:
                        advanceplanner.update_logfile_agenda(planner.weekfile, dayagenda)
                    filesystem.write_planner_to_filesystem(planner, wikidir)
                if err.status >= utils.PlannerPeriod.Week:
                    planner = filesystem.construct_planner_from_filesystem(wikidir)
                    weekagenda = advanceplanner.extract_agenda_from_logfile(planner.weekfile)
                    if weekagenda:
                        advanceplanner.update_logfile_agenda(planner.monthfile, weekagenda)
                    filesystem.write_planner_to_filesystem(planner, wikidir)
                simulate = False
            except DayStillInProgressError as err:
                print("Current day is still in progress! Try again after 6pm.")
                break
            except PlannerIsInTheFutureError as err:
                raise
            except TomorrowIsEmptyError as err:
                yn = raw_input("The tomorrow section is blank. Do you want to add some tasks for tomorrow? [y/n]__")
                if yn.lower().startswith('y'):
                    raw_input('No problem. Press any key when you are done adding tasks...')
                elif yn.lower().startswith('n'):
                    config.PlannerConfig.TomorrowChecking = config.LOGFILE_CHECKING['LAX']
                else:
                    continue
            except LogfileNotCompletedError as err:
                yn = raw_input("Looks like you haven't completed your %s's log (e.g. NOTES). Would you like to do that now? [y/n]__" % err.period)
                if yn.lower().startswith('y'):
                    raw_input('No problem. Press any key when you are done completing your log...')
                elif yn.lower().startswith('n'):
                    config.PlannerConfig.LogfileCompletionChecking = config.LOGFILE_CHECKING['LAX']
                else:
                    continue
            except DateFormatError as err:
                raise
            except BlockedTaskNotScheduledError as err:
                raise
            except TasklistLayoutError as err:
                raise
            except LogfileLayoutError as err:
                raise
            except PlannerStateError as err:
                raise
            except RelativeDateError as err:
                raise


if __name__ == '__main__':
    main()

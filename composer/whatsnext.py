#!/usr/bin/env python

import datetime
import os
from subprocess import call

import click

from . import advice
from . import config
from . import updateindex
from . import utils
from .backend import FilesystemPlanner

from .errors import (
    SchedulingError,
    DayStillInProgressError,
    LayoutError,
    LogfileNotCompletedError,
    PlannerStateError,
    SimulationPassedError,
    TomorrowIsEmptyError,
)

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO

try:  # py2
    raw_input
except NameError:  # py3
    raw_input = input

CONFIG_ROOT = os.getenv("COMPOSER_ROOT", os.path.expanduser("~/.composer"))
CONFIG_FILE = os.path.join(CONFIG_ROOT, "config.ini")


def process_wiki(wikidir, preferences, now):
    simulate = True
    while True:
        try:
            planner = FilesystemPlanner(wikidir)
            planner.set_preferences(preferences)
            planner.advance(now=now, simulate=simulate)
            print()
            print(
                "Moving tasks added for tomorrow over to"
                " tomorrow's agenda..."
            )
            print(
                "Carrying over any unfinished tasks from today"
                " to tomorrow's agenda..."
            )
            print(
                "Checking for any other tasks previously scheduled "
                "for tomorrow..."
            )
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
            plannerdate = FilesystemPlanner(wikidir).date
            (date, month, year) = (
                plannerdate.day,
                plannerdate.strftime("%B"),
                plannerdate.year,
            )
            datestr = "%s %d, %d" % (month, date, year)
            with open(os.devnull, "w") as null:
                call(["git", "add", "-A"], cwd=wikidir, stdout=null)
                call(
                    ["git", "commit", "-m", "SOD %s" % datestr],
                    cwd=wikidir,
                    stdout=null,
                )
            print("...DONE.")
            print()
            print("~~~ THOUGHT FOR THE DAY ~~~")
            print()
            filepaths = map(
                lambda f: wikidir + "/" + f, preferences["lessons_files"]
            )

            def openfile(fn):
                try:
                    f = open(fn, "r")
                except Exception:
                    f = StringIO("")
                return f

            lessons_files = map(openfile, filepaths)
            print(advice.get_advice(lessons_files))
            if (
                planner.jumping
            ):  # if jumping, keep repeating until present-day error thrown
                simulate = True
            else:
                break
        except SimulationPassedError as err:
            # print "DEV: simulation passed. let's do this thing
            # ... for real."
            if err.status >= utils.PlannerPeriod.Week:
                theme = raw_input(
                    "(Optional) Enter a theme for the upcoming week,"
                    " e.g. Week of 'Timeliness', or 'Completion':__"
                )
                planner.week_theme = theme if theme else None
            if err.status >= utils.PlannerPeriod.Day:
                # git commit a "before", now that we know changes
                # are about to be written to planner
                print()
                print("Saving EOD planner state before making changes...")
                plannerdate = FilesystemPlanner(wikidir).date
                (date, month, year) = (
                    plannerdate.day,
                    plannerdate.strftime("%B"),
                    plannerdate.year,
                )
                datestr = "%s %d, %d" % (month, date, year)
                with open(os.devnull, "w") as null:
                    call(["git", "add", "-A"], cwd=wikidir, stdout=null)
                    call(
                        ["git", "commit", "-m", "EOD %s" % datestr],
                        cwd=wikidir,
                        stdout=null,
                    )
                print("...DONE.")
            if err.status >= utils.PlannerPeriod.Day:
                planner = FilesystemPlanner(wikidir)
                dayagenda = planner.get_agenda(planner.dayfile)
                if dayagenda:
                    planner.weekfile = planner.update_agenda(
                        planner.weekfile, dayagenda
                    )
                planner.save()
            if err.status >= utils.PlannerPeriod.Week:
                planner = FilesystemPlanner(wikidir)
                weekagenda = planner.get_agenda(planner.weekfile)
                if weekagenda:
                    planner.monthfile = planner.update_agenda(
                        planner.monthfile, weekagenda
                    )
                planner.save()
            simulate = False
        except TomorrowIsEmptyError as err:
            yn = raw_input(
                "The tomorrow section is blank. Do you want to add"
                " some tasks for tomorrow? [y/n]__"
            )
            if yn.lower().startswith("y"):
                raw_input(
                    "No problem. Press any key when you are done"
                    " adding tasks..."
                )
            elif yn.lower().startswith("n"):
                planner.tomorrow_checking = config.LOGFILE_CHECKING["LAX"]
            else:
                continue
        except LogfileNotCompletedError as err:
            yn = raw_input(
                "Looks like you haven't completed your %s's log"
                " (e.g. NOTES). Would you like to do that now? [y/n]__"
                % err.period
            )
            if yn.lower().startswith("y"):
                raw_input(
                    "No problem. Press any key when you are done"
                    " completing your log..."
                )
            elif yn.lower().startswith("n"):
                planner.logfile_completion_checking = config.LOGFILE_CHECKING[
                    "LAX"
                ]
            else:
                continue
        except DayStillInProgressError as err:
            print("Current day is still in progress! Try again after 6pm.")
            break
        except PlannerStateError as err:
            raise
        except SchedulingError as err:
            raise
        except LayoutError as err:
            raise


@click.command(
    help=(
        "Move on to the next thing in your planning, organizing, "
        "and tracking workflow.\n"
        "WIKIPATH is the path of the wiki to operate on.\n"
        "If not provided, uses the path(s) specified in "
        "config.ini"
    )
)
@click.argument("wikipath", required=False)
@click.option(
    "-t",
    "--test",
    is_flag=True,
    help=("A temporary flag for testing. To be removed in a future version."),
)
@click.option("-j", "--jump", is_flag=True, help="Jump to present day.")
def main(wikipath=None, test=False, jump=False):
    # Moved pending tasks from today over to tomorrow's agenda
    # could try: [Display score for today]

    now = None

    preferences = config.read_user_preferences(CONFIG_FILE)
    # if wikipath is specified, it should override
    # the configured paths in the ini file
    if wikipath:
        wikidirs = [wikipath]
    else:
        wikidirs = preferences["wikis"]
    if test:
        # so jump can be tested on test wiki
        now = datetime.datetime(2013, 1, 8, 19, 0, 0)

    if jump:
        preferences.jump = jump
        print()
        print(">>> Get ready to JUMP! <<<")
        print()

    # simulate the changes first and then when it's all OK, make the necessary
    # preparations (e.g. git commit) and actually perform the changes

    for wikidir in wikidirs:
        print()
        print(">>> Operating on planner at location: %s <<<" % wikidir)
        print()
        process_wiki(wikidir, preferences, now)


if __name__ == "__main__":
    main()

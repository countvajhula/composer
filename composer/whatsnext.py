#!/usr/bin/env python

import datetime
import os
from subprocess import call

import click

from . import advice
from . import config
from . import updateindex
from .backend import (
    FilesystemPlanner,
    FilesystemTasklist,
    get_month_name,
    quarter_for_month,
)
from .timeperiod import (
    Day,
    Month,
    Quarter,
    Week,
    Year,
    get_next_period,
    get_next_day,
)
from .utils import display_message, ask_input

from .errors import (
    AgendaNotReviewedError,
    SchedulingError,
    LayoutError,
    LogfileNotCompletedError,
    PlannerStateError,
    MissingThemeError,
)

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO

CONFIG_ROOT = os.getenv("COMPOSER_ROOT", os.path.expanduser("~/.composer"))
CONFIG_FILE = os.path.join(CONFIG_ROOT, config.CONFIG_FILENAME)


def _make_git_commit(wikidir, message):
    with open(os.devnull, "w") as null:
        call(["git", "add", "-A"], cwd=wikidir, stdout=null)
        call(["git", "commit", "-m", message], cwd=wikidir, stdout=null)


def _show_advice(wikidir, preferences):
    display_message("~~~ THOUGHT FOR THE DAY ~~~")
    display_message()
    filepaths = map(lambda f: wikidir + "/" + f, preferences["lessons_files"])

    def openfile(fn):
        try:
            f = open(fn, "r")
        except Exception:
            f = StringIO("")
        return f

    lessons_files = map(openfile, filepaths)
    display_message(advice.get_advice(lessons_files))


def _post_advance_tasks(wikidir, plannerdate, preferences):
    """ Update the index to include any newly created files,
    Commit the post-advance state into git, and display a
    thought for the day.
    """
    # update index after making changes
    display_message()
    display_message("Updating planner wiki index", interactive=True)
    updateindex.update_index(wikidir)
    # git commit "after"
    display_message()
    display_message("Committing all changes", interactive=True)
    (date, month, year) = (
        plannerdate.day,
        plannerdate.strftime("%B"),
        plannerdate.year,
    )
    datestr = "%s %d, %d" % (month, date, year)
    message = "SOD %s" % datestr
    _make_git_commit(wikidir, message)

    display_message()
    _show_advice(wikidir, preferences)


def process_wiki(wikidir, preferences, now):
    """ Advance the wiki at the specified path, according to any configured
    preferences.

    :param str wikidir: The path to the wiki
    :param dict preferences: User preferences e.g. from a config file
    :param :class:`datetime.datetime` now: The time to treat as current real
        world time. Not sure if it's used for anything aside from testing the
        jump feature
    """
    # simulate the changes first and then when it's all OK, make the necessary
    # preparations (e.g. git commit) and actually perform the changes
    display_message()
    display_message(">>> Operating on planner at location: %s <<<" % wikidir)

    config.update_wiki_specific_preferences(
        wikidir, preferences
    )  # mutates preferences

    while True:
        display_message()
        try:
            tasklist = FilesystemTasklist(wikidir)
            planner = FilesystemPlanner(wikidir, tasklist)
            planner.set_preferences(preferences)
            status, next_day_planner = planner.advance(now=now)
        except LogfileNotCompletedError as err:
            display_message(
                "Looks like you haven't completed your %s's log"
                " (e.g. NOTES). Would you like to do that now? [y/n]__"
                % err.period,
                newline=False,
                prompt=True,
            )
            yn = ask_input()
            if yn.lower().startswith("y"):
                display_message(
                    "No problem. Press any key when you are done"
                    " completing your log.",
                    newline=False,
                    prompt=True,
                )
                ask_input()
            elif yn.lower().startswith("n"):
                preferences[
                    'logfile_completion_checking'
                ] = config.LOGFILE_CHECKING["LAX"]
            else:
                continue
        except PlannerStateError as err:
            raise
        except SchedulingError as err:
            raise
        except LayoutError as err:
            raise
        except MissingThemeError as err:
            display_message(
                "(Optional) Enter a theme for the upcoming {period}, "
                "e.g. {period_cap} of 'Timeliness', "
                "or 'Completion':__".format(
                    period=err.period, period_cap=str(err.period).capitalize()
                ),
                newline=False,
                prompt=True,
            )
            theme = ask_input()
            preferences[
                "week_theme"
            ] = theme  # empty string if the user entered nothing
        except AgendaNotReviewedError as err:
            next_day = get_next_day(planner.date)
            next_period = (
                get_next_period(err.period) if err.period < Year else Year
            )
            month_name = get_month_name(next_day.month)
            if err.period == Day:
                period_string = "tomorrow"
            elif err.period == Week:
                period_string = "next {period}".format(period=err.period)
            elif err.period == Month:
                period_string = month_name
            elif err.period == Quarter:
                month = get_month_name(next_day.month)
                period_string = quarter_for_month(month_name)
            elif err.period == Year:
                period_string = str(next_day.year)

            display_message(
                "This is what you have lined up for {period} "
                "at the moment:".format(period=period_string)
            )
            display_message(err.agenda)
            display_message(
                "Does that look good? [y/n]__", newline=False, prompt=True
            )
            yn = ask_input()
            if yn.lower().startswith("y"):
                preferences["agenda_reviewed"] = err.period
            elif yn.lower().startswith("n"):
                display_message(
                    "Go ahead and pull in any {next_period} tasks "
                    "that you'd like to work on {this_period}, or make any "
                    "other changes you'd like. Press any key when you are "
                    "done.".format(
                        next_period="of this {}'s".format(next_period)
                        if err.period < Year
                        else "unscheduled",
                        this_period="next {period}".format(period=err.period)
                        if err.period > Day
                        else "tomorrow",
                    ),
                    newline=False,
                    prompt=True,
                )
                ask_input()

        else:
            # print "DEV: simulation passed. let's do this thing
            # ... for real."
            if status >= Day:
                # git commit a "before", now that we know changes
                # are about to be written to planner
                display_message()
                display_message(
                    "Saving EOD planner state before making changes",
                    interactive=True,
                )
                plannerdate = planner.date
                (date, month, year) = (
                    plannerdate.day,
                    plannerdate.strftime("%B"),
                    plannerdate.year,
                )
                datestr = "%s %d, %d" % (month, date, year)
                message = "EOD %s" % datestr
                _make_git_commit(wikidir, message)

                # actually make the changes on disk. No changes should
                # have been persisted up to this point
                try:
                    # check for possible errors in planner state before making
                    # any changes if errors are found, an exception is raised
                    # and no changes are made
                    next_day_planner.is_ok_to_advance(status)
                except PlannerStateError:
                    raise

                # no going back now -- everything is expected to work without
                # error past this point

                # save all existing periods that advanced, and also one
                # higher period to account for the advance of contained
                # periods
                next_period = (
                    get_next_period(status) if status < Year else status
                )
                planner.save(next_period)

                # save all newly advanced periods
                next_day_planner.save(status)

                # save the (common) tasklist
                planner.tasklist.save()

                _post_advance_tasks(
                    wikidir, next_day_planner.date, preferences
                )
                if (
                    planner.jumping
                ):  # if jumping, keep repeating until present-day error thrown
                    preferences['week_theme'] = None  # reset week theme
                else:
                    break
            else:
                display_message(
                    "Current day is still in progress! Try again after 6pm."
                )
                break


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
        preferences['jump'] = jump
        display_message()
        display_message(">>> Get ready to JUMP! <<<")
        display_message()
        ask_input()

    for wikidir in wikidirs:
        process_wiki(
            wikidir,
            preferences.copy(),  # contain any wiki-specific modifications
            now,
        )


if __name__ == "__main__":
    main()

#!/usr/bin/env python

import os
from subprocess import call

import click

from . import advice
from . import config
from . import updateindex
from .cache import read_cache, archive_cache
from .backend import FilesystemPlanner, FilesystemTasklist
from .timeperiod import (
    Zero,
    Day,
    Month,
    Quarter,
    Week,
    Year,
    get_next_period,
    quarter_for_month,
    get_month_name,
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
    display_message()
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


def _pass_baton(wikidir, preferences):
    """Display the contents of the "baton" file (usually Cache.wiki)
    as the strands in progress / next steps to pick up on. Then clear
    the file.
    """
    cache_file = preferences.get('cache_file')
    if cache_file:
        cache_path = os.path.join(wikidir, cache_file)
        archive_cache_file = "Archive_" + cache_file
        archive_cache_path = os.path.join(wikidir, archive_cache_file)
        notes = read_cache(cache_path)
        if notes:
            # display its contents
            display_message()
            display_message("~~~ YOUR NOTES FROM YESTERDAY ~~~")
            display_message()
            display_message(notes)
            # move it to the archive
            archive_cache(cache_path, archive_cache_path)


def _post_advance_tasks(wikidir, plannerdate, preferences):
    """Update the index to include any newly created files,
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

    _pass_baton(wikidir, preferences)

    _show_advice(wikidir, preferences)


def process_wiki(wikidir, preferences):
    """Advance the wiki at the specified path, according to any configured
    preferences.

    :param str wikidir: The path to the wiki
    :param dict preferences: User preferences e.g. from a config file
    """
    # simulate the changes first and then when it's all OK, make the necessary
    # preparations (e.g. git commit) and actually perform the changes
    display_message()
    display_message(">>> Operating on planner at location: %s <<<" % wikidir)

    config.update_wiki_specific_preferences(
        wikidir, preferences
    )  # mutates preferences

    period_prompted = Zero
    while True:
        display_message()
        try:
            tasklist = FilesystemTasklist(wikidir)
            planner = FilesystemPlanner(wikidir, tasklist, preferences)
            status, next_day_planner = planner.advance()
        except LogfileNotCompletedError as err:
            display_message(
                "Looks like you haven't completed your %s's log"
                " (e.g. NOTES). Would you like to do that now? [y/n]__"
                % err.period,
                newline=False,
                prompt=True,
                interrupt=True,
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
        except PlannerStateError:
            raise
        except SchedulingError as err:
            display_message(err.value, newline=False, prompt=True)
            ask_input()
        except LayoutError:
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
                interrupt=True,
            )
            theme = ask_input()
            preferences[
                "week_theme"
            ] = theme  # empty string if the user entered nothing
        except AgendaNotReviewedError as err:
            next_day = planner.next_day()
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
                period_string = quarter_for_month(next_day.month)
            elif err.period == Year:
                period_string = str(next_day.year)

            if err.period > Day and period_prompted < err.period:
                display_message(
                    "It's time to review {next_period} tasks and identify any "
                    "that you'd like to work on {this_period}.".format(
                        next_period="this {}'s".format(next_period)
                        if err.period < Year
                        else "unscheduled",
                        this_period="next {period}".format(period=err.period)
                        if err.period > Day
                        else "tomorrow",
                    ),
                    prompt=True,
                    interrupt=True,
                    acknowledge=True,
                )
                period_prompted = err.period
            display_message(
                "This is what you have lined up for {period} "
                "at the moment:".format(period=period_string),
                prompt=True,
                interrupt=True,
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
            else:
                display_message(
                    "Current day is still in progress! Try again after 6pm."
                )
            break


# TODO: support version
# TODO: help text for jump and other flags
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
@click.option("-j", "--jump", is_flag=True, help="Jump to present day.")
def main(wikipath=None, jump=False):
    # could try: [Display score for today]

    preferences = config.read_user_preferences(CONFIG_FILE)
    # if wikipath is specified, it should override
    # the configured paths in the ini file
    if wikipath:
        wikidirs = [wikipath]
    else:
        wikidirs = preferences["wikis"]

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
        )


if __name__ == "__main__":
    main()

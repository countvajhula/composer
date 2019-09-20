#!/usr/bin/env python

""" Just a hacked-together script to collect notes from the present
week, month, ..., to help save time on retrospectives """

import os
import re

import click

from datetime import timedelta

from composer.backend import FilesystemPlanner
from composer.backend.filesystem.interface import get_constituent_logs
from composer.backend.filesystem.primitives import get_log_filename
from composer.utils import display_message
from composer.timeperiod import Week, Month, Quarter, get_next_period
from composer import config

CONFIG_ROOT = os.getenv("COMPOSER_ROOT", os.path.expanduser("~/.composer"))
CONFIG_FILE = os.path.join(CONFIG_ROOT, config.CONFIG_FILENAME)


def get_filename(wikidir, filelink):
    flink = "%s/%s" % (wikidir, filelink)
    return os.readlink(flink)


def extract_log_time_from_text(logtext):
    notes_idx = re.search(r"NOTES:\n", logtext).end()
    end_idx = re.search(r"\nTIME", logtext).start()
    log = logtext[notes_idx:end_idx].strip(" \n")
    time_idx = end_idx + logtext[end_idx:].find(":") + 1
    time = logtext[time_idx:].strip(" \n")
    return (log, time)


def get_logs_times(wikidir, period):
    """ read currentweek link as filename;
    parse out first day of week from filename;
    open days in order and re search for NOTES. Extract until ^TIME
    exit on file not found error
    return notes separated by lines and headed by dates
    """
    planner = FilesystemPlanner(wikidir)
    logs = get_constituent_logs(period, planner.date, wikidir)
    constituent_period = get_next_period(period, decreasing=True)
    (logs_string, times) = ("", [])
    current_date = period.get_start_date(planner.date)
    for log in logs:
        (log, time) = extract_log_time_from_text(log.read())
        start_date = constituent_period.get_start_date(current_date)
        logs_string += (
            get_log_filename(start_date, constituent_period)
            + "\n"
            + log
            + "\n\n"
        )
        times.append(time)
        current_date = constituent_period.get_end_date(
            current_date
        ) + timedelta(days=1)
    return (logs_string, times)


def get_logs_times_this_week(wikidir):
    return get_logs_times(wikidir, Week)


def get_logs_times_this_month(wikidir):
    """ read currentmonth link as filename;
    parse out first week of month from filename;
    open weeks in order and re search for NOTES. Extract until ^TIME
    exit on file not found error
    return notes separated by lines and headed by dates
    """
    return get_logs_times(wikidir, Month)


def get_logs_times_this_quarter(wikidir):
    """ read currentquarter link as filename;
    parse out first month of quarter from filename;
    open months in order and re search for NOTES. Extract until ^TIME
    exit on file not found error
    return notes separated by lines and headed by dates
    """
    return get_logs_times(wikidir, Quarter)


@click.command(
    help=(
        "Collect recent log data to help with retrospectives.\n"
        "WIKIPATH is the path of the wiki to operate on.\n"
        "If not provided, uses the path(s) specified in "
        "config.ini"
    )
)
@click.argument("wikipath", required=False)
def main(wikipath=None):
    preferences = config.read_user_preferences(CONFIG_FILE)
    # if wikipath is specified, it should override
    # the configured paths in the ini file
    if wikipath:
        wikidirs = [wikipath]
    else:
        wikidirs = preferences["wikis"]
    for wikidir in wikidirs:
        (weeklogs, weektimes) = get_logs_times_this_week(wikidir)
        (monthlogs, monthtimes) = get_logs_times_this_month(wikidir)
        (quarterlogs, quartertimes) = get_logs_times_this_quarter(wikidir)
        display_message("Daily logs for the past week (%s)" % wikidir)
        display_message(weeklogs)
        display_message("Daily Times:")
        display_message(weektimes)
        display_message()
        display_message("Weekly logs for the past month (%s)" % wikidir)
        display_message(monthlogs)
        display_message("Weekly Times:")
        display_message(monthtimes)
        display_message()
        display_message("Monthly logs for the past quarter (%s)" % wikidir)
        display_message(quarterlogs)
        display_message("Monthly Times:")
        display_message(quartertimes)
        display_message()


if __name__ == "__main__":
    main()

#!/usr/bin/env python

""" Just a hacked-together script to collect notes from the present
week, month, ..., to help save time on retrospectives """

import os

import click

from datetime import timedelta

from composer.backend import FilesystemPlanner
from composer.backend.filesystem.interface import (
    get_constituent_logs,
    compute_time_spent_on_planner,
)
from composer.backend.filesystem.primitives import (
    get_log_filename,
    read_section,
)
from composer.backend.filesystem.date_parsers import parse_dateformat12
from composer.utils import display_message
from composer.timeperiod import Week, Month, Quarter, Year, get_next_period
from composer import config

CONFIG_ROOT = os.getenv("COMPOSER_ROOT", os.path.expanduser("~/.composer"))
CONFIG_FILE = os.path.join(CONFIG_ROOT, config.CONFIG_FILENAME)


def extract_notes_from_log(logfile):
    """Given the contents of a log file, return the contents of the notes
    section.

    :param str logfile: The log file
    :returns str: The notes
    """
    notes, _ = read_section(logfile, "notes")
    return notes.read().strip()


def get_logs_times(wikidir, period, reference_date=None):
    """Get constituent log notes and time spent for the specified period.
    E.g. for a month, this would return the notes and times for each contained
    week.  Return notes separated by lines and headed by dates.

    :param str wikidir: The path to the planner wiki
    :param :class:`~composer.timeperiod.Period` period: A
    :returns tuple: The logs (str) and times (list)
    """
    planner = FilesystemPlanner(wikidir)
    reference_date = reference_date or planner.date
    current_date = period.get_start_date(reference_date)
    logs = get_constituent_logs(period, current_date, wikidir)
    constituent_period = get_next_period(period, decreasing=True)
    logs_string = ""
    time = compute_time_spent_on_planner(period, current_date, wikidir)
    # hrs, mins
    for log in logs:
        notes = extract_notes_from_log(log)
        start_date = constituent_period.get_start_date(current_date)
        # TODO: in case of missing logs, this mislabels the
        # log period. Instead, rely on get_constituent_logs to
        # provide source information instead of independently
        # computing things here
        logs_string += (
            get_log_filename(start_date, constituent_period)
            + "\n"
            + notes
            + "\n\n"
        )
        current_date = constituent_period.get_end_date(
            current_date
        ) + timedelta(days=1)
    return (logs_string, time)


@click.command(
    help=(
        "Collect recent log data to help with retrospectives.\n"
        "WIKIPATH is the path of the wiki to operate on.\n"
        "If not provided, uses the path(s) specified in "
        "config.ini"
    )
)
@click.argument("wikipath", required=False)
@click.option("-d", "--date", help="Reference date to use (MM-DD-YYYY).")
def main(wikipath=None, date=None):
    preferences = config.read_user_preferences(CONFIG_FILE)
    # if wikipath is specified, it should override
    # the configured paths in the ini file
    if wikipath:
        wikidirs = [wikipath]
    else:
        wikidirs = preferences["wikis"]
    if date:
        date = parse_dateformat12(date)[0]
    for wikidir in wikidirs:
        (daylogs, (week_hr, week_min)) = get_logs_times(wikidir, Week, date)
        (weeklogs, (month_hr, month_min)) = get_logs_times(
            wikidir, Month, date
        )
        (monthlogs, (quarter_hr, quarter_min)) = get_logs_times(
            wikidir, Quarter, date
        )
        (quarterlogs, (year_hr, year_min)) = get_logs_times(
            wikidir, Year, date
        )
        display_message("Daily logs for the past week (%s)" % wikidir)
        display_message(daylogs)
        display_message("Time spent this week:")
        display_message(str(week_hr) + " hrs " + str(week_min) + " mins")
        display_message()
        display_message("Weekly logs for the past month (%s)" % wikidir)
        display_message(weeklogs)
        display_message("Time spent this month:")
        display_message(str(month_hr) + " hrs " + str(month_min) + " mins")
        display_message()
        display_message("Monthly logs for the past quarter (%s)" % wikidir)
        display_message(monthlogs)
        display_message("Time spent this quarter:")
        display_message(str(quarter_hr) + " hrs " + str(quarter_min) + " mins")
        display_message()
        display_message("Quarterly logs for the past year (%s)" % wikidir)
        display_message(quarterlogs)
        display_message("Time spent this year:")
        display_message(str(year_hr) + " hrs " + str(year_min) + " mins")
        display_message()


if __name__ == "__main__":
    main()

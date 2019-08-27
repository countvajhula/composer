#!/usr/bin/env python

""" Just a hacked-together script to collect notes from the present
week, month, ..., to help save time on retrospectives """

import datetime
import os
import re

import click

from composer.backend import FilesystemPlanner
from composer.backend.filesystem.utils import read_file
from composer.utils import display_message
from composer.timeperiod import Week
from composer import config

CONFIG_ROOT = os.getenv("COMPOSER_ROOT", os.path.expanduser("~/.composer"))
CONFIG_FILE = os.path.join(CONFIG_ROOT, "config.ini")

PLANNERDAYFILELINK = "currentday"
PLANNERWEEKFILELINK = "currentweek"
PLANNERMONTHFILELINK = "currentmonth"
PLANNERQUARTERFILELINK = "currentquarter"


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


def get_logs_times_this_week(wikidir):
    """ read currentweek link as filename;
    parse out first day of week from filename;
    open days in order and re search for NOTES. Extract until ^TIME
    exit on file not found error
    return notes separated by lines and headed by dates
    """
    planner = FilesystemPlanner(wikidir)
    (logs, times) = ("", [])
    fn = get_filename(wikidir, PLANNERWEEKFILELINK)
    startday_str = re.search(
        r"[^\.]*", fn[8:]
    ).group()  # confirm what group does
    planner.date = datetime.datetime.strptime(startday_str, "%B %d, %Y").date()
    fnpath = "%s/%s.wiki" % (
        wikidir,
        planner.date.strftime("%B %d, %Y").replace(" 0", " "),
    )
    while True:
        try:
            logtext = read_file(fnpath)
        except Exception:
            break
        (log, time) = extract_log_time_from_text(logtext)
        logs += str(planner.date) + "\n" + log + "\n\n"
        times.append(time)
        planner.date += datetime.timedelta(days=1)
        fnpath = "%s/%s.wiki" % (
            wikidir,
            planner.date.strftime("%B %d, %Y").replace(" 0", " "),
        )  # handle "January 01" as "January 1"
    return (logs, times)


def get_logs_times_this_month(wikidir):
    """ read currentmonth link as filename;
    parse out first week of month from filename;
    open weeks in order and re search for NOTES. Extract until ^TIME
    exit on file not found error
    return notes separated by lines and headed by dates
    """
    planner = FilesystemPlanner(wikidir)
    (logs, times) = ("", [])
    fn = get_filename(wikidir, PLANNERMONTHFILELINK)
    month = fn.split()[2].strip(",")
    startday_str = month + " 1, " + fn.split()[3][0:4]
    planner.date = datetime.datetime.strptime(startday_str, "%B %d, %Y").date()
    fnpath = "%s/Week of %s.wiki" % (
        wikidir,
        planner.date.strftime("%B %d, %Y").replace(" 0", " "),
    )
    while True:
        try:
            logtext = read_file(fnpath)
        except Exception:
            break
        (log, time) = extract_log_time_from_text(logtext)
        logs += "Week of " + str(planner.date) + "\n" + log + "\n\n"
        times.append(time)
        planner.date += datetime.timedelta(days=1)
        while not Week.advance_criteria_met(planner, datetime.datetime.now()):
            planner.date += datetime.timedelta(days=1)
        planner.date += datetime.timedelta(
            days=1
        )  # next day is the one we're looking for
        fnpath = "%s/Week of %s.wiki" % (
            wikidir,
            planner.date.strftime("%B %d, %Y").replace(" 0", " "),
        )
    return (logs, times)


def get_logs_times_this_quarter(wikidir):
    """ read currentquarter link as filename;
    parse out first month of quarter from filename;
    open months in order and re search for NOTES. Extract until ^TIME
    exit on file not found error
    return notes separated by lines and headed by dates
    """
    planner = FilesystemPlanner(wikidir)
    (logs, times) = ("", [])
    fn = get_filename(wikidir, PLANNERQUARTERFILELINK)
    quarter = fn.split()[0]
    if quarter == "Q1":
        month = "January"
    elif quarter == "Q2":
        month = "April"
    elif quarter == "Q3":
        month = "July"
    elif quarter == "Q4":
        month = "October"
    else:
        raise Exception(
            "Quarter filename not recognized! Must be e.g. 'Q1 2014'"
        )
    startmonth_str = month + ", " + fn.split()[1][0:4]
    planner.date = datetime.datetime.strptime(startmonth_str, "%B, %Y").date()
    fnpath = "%s/Month of %s.wiki" % (wikidir, planner.date.strftime("%B, %Y"))
    while True:
        try:
            logtext = read_file(fnpath)
        except Exception:
            break
        (log, time) = extract_log_time_from_text(logtext)
        logs += (
            "Month of " + planner.date.strftime("%B, %Y") + "\n" + log + "\n\n"
        )
        times.append(time)
        if planner.date.month < 12:
            planner.date = datetime.date(
                planner.date.year, planner.date.month + 1, planner.date.day
            )
        else:
            planner.date = datetime.date(
                planner.date.year + 1, 1, planner.date.day
            )
        fnpath = "%s/Month of %s.wiki" % (
            wikidir,
            planner.date.strftime("%B, %Y"),
        )
    return (logs, times)


@click.command(help=("Collect recent log data to help with retrospectives."))
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

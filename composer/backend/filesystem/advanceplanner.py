#!/usr/bin/env python

import datetime

from ... import config
from ...errors import (
    DayStillInProgressError,
    LogfileLayoutError,
    LogfileNotCompletedError,
    PlannerIsInTheFutureError,
)
from . import templates
from ...timeperiod import (
    Day,
    Week,
    Month,
    Quarter,
    Year,
    Zero,
    PeriodAdvanceCriteria,
    get_next_day,
)
from .utils import read_section


def check_logfile_completion(logfile):
    """ Check the logfile's NOTES section as a determination of whether
    the log has been completed """
    completed = False
    try:
        notes, _ = read_section(logfile, 'notes')
    except ValueError:
        raise LogfileLayoutError(
            "Error: No 'NOTES' section found in your log file!"
        )
    notes = notes.read()
    if notes.strip("\n ") != "":
        completed = True
    return completed


def _next_period(current_period):
    periods = (Zero, Day, Week, Month, Quarter, Year)
    try:
        index = periods.index(current_period)
        next_period = periods[index + 1]
    except (IndexError, ValueError):
        raise
    return next_period


def advance_planner(planner, now=None):
    """ Advance planner state to next day, updating week and month info
    as necessary. 'now' arg used only for testing
    """
    next_day = get_next_day(planner.date)  # the new day to advance to

    if not now:
        now = datetime.datetime.now()

    def advance_period(current_period):
        """ Recursive function to advance planner by day, week, month, quarter, or year
        as the case may be.
        """
        next_period = _next_period(current_period)
        period_criteria_met = next_period.advance_criteria_met(planner, now)
        if period_criteria_met == PeriodAdvanceCriteria.Satisfied:
            current_period = next_period
            logfile = current_period.get_logfile(planner)
            if planner.logfile_completion_checking == config.LOGFILE_CHECKING[
                "STRICT"
            ] and not check_logfile_completion(logfile):
                periodstr = current_period.get_name()
                msg = (
                    "Looks like you haven't completed your %s's log."
                    " Would you like to do that now?" % periodstr
                )
                raise LogfileNotCompletedError(msg, periodstr)
            templates.write_new_template(planner, current_period, next_day)

            if current_period < Year:
                return advance_period(current_period)
        elif period_criteria_met == PeriodAdvanceCriteria.DayStillInProgress:
            raise DayStillInProgressError(
                "Current day is still in progress! Update after 6pm"
            )
        elif period_criteria_met == PeriodAdvanceCriteria.PlannerInFuture:
            raise PlannerIsInTheFutureError("Planner is in the future!")
        else:
            templates.write_existing_template(planner, next_period, next_day)
        return current_period

    status = advance_period(Zero)
    if status > Zero:
        planner.date = next_day

    return status

#!/usr/bin/env python

from composer.backend import FilesystemPlanner, FilesystemTasklist
from composer.timeperiod import (
    Day,
    Week,
    Month,
    Quarter,
    Year,
    get_next_period,
)


def test_advance_planner_day():
    """Actually operate on a wiki that's configured such that only a day
    advance is in order. After running the test check that this is what has
    happened (git status / diff if git managed test wikis)
    """
    WIKIPATH = 'tests/testwikis/daywiki'
    tasklist = FilesystemTasklist(WIKIPATH)
    planner = FilesystemPlanner(WIKIPATH, tasklist)
    preferences = {'week_theme': '', 'agenda_reviewed': Day}
    planner.set_preferences(preferences)
    status, next_day_planner = planner.advance()
    next_period = get_next_period(status) if status < Year else status
    planner.save(next_period)
    next_day_planner.save(status)
    planner.tasklist.save()
    assert status == Day


def test_advance_planner_week():
    """Actually operate on a wiki that's configured such that a week
    advance is in order. After running the test check that this is what has
    happened (git status / diff if git managed test wikis)
    """
    WIKIPATH = 'tests/testwikis/weekwiki'
    tasklist = FilesystemTasklist(WIKIPATH)
    planner = FilesystemPlanner(WIKIPATH, tasklist)
    preferences = {'week_theme': '', 'agenda_reviewed': Week}
    planner.set_preferences(preferences)
    status, next_day_planner = planner.advance()
    next_period = get_next_period(status) if status < Year else status
    planner.save(next_period)
    next_day_planner.save(status)
    planner.tasklist.save()
    assert status == Week


def test_advance_planner_month():
    """Actually operate on a wiki that's configured such that a month
    advance is in order. After running the test check that this is what has
    happened (git status / diff if git managed test wikis)
    """
    WIKIPATH = 'tests/testwikis/monthwiki'
    tasklist = FilesystemTasklist(WIKIPATH)
    planner = FilesystemPlanner(WIKIPATH, tasklist)
    preferences = {'week_theme': '', 'agenda_reviewed': Month}
    planner.set_preferences(preferences)
    status, next_day_planner = planner.advance()
    next_period = get_next_period(status) if status < Year else status
    planner.save(next_period)
    next_day_planner.save(status)
    planner.tasklist.save()
    assert status == Month


def test_advance_planner_quarter():
    """Actually operate on a wiki that's configured such that a quarter
    advance is in order. After running the test check that this is what has
    happened (git status / diff if git managed test wikis)
    """
    WIKIPATH = 'tests/testwikis/quarterwiki'
    tasklist = FilesystemTasklist(WIKIPATH)
    planner = FilesystemPlanner(WIKIPATH, tasklist)
    preferences = {'week_theme': '', 'agenda_reviewed': Quarter}
    planner.set_preferences(preferences)
    status, next_day_planner = planner.advance()
    next_period = get_next_period(status) if status < Year else status
    planner.save(next_period)
    next_day_planner.save(status)
    planner.tasklist.save()
    assert status == Quarter


def test_advance_planner_year():
    """Actually operate on a wiki that's configured such that a year
    advance is in order. After running the test check that this is what has
    happened (git status / diff if git managed test wikis)
    """
    WIKIPATH = 'tests/testwikis/yearwiki'
    tasklist = FilesystemTasklist(WIKIPATH)
    planner = FilesystemPlanner(WIKIPATH, tasklist)
    preferences = {'week_theme': '', 'agenda_reviewed': Year}
    planner.set_preferences(preferences)
    status, next_day_planner = planner.advance()
    next_period = get_next_period(status) if status < Year else status
    planner.save(next_period)
    next_day_planner.save(status)
    planner.tasklist.save()
    assert status == Year

import datetime


class PlannerPeriod(object):
    (Zero, Day, Week, Month, Quarter, Year) = (0, 1, 2, 3, 4, 5)


class PlannerUserSettings(object):
    WeekTheme = None


class PlannerConfig(object):
    (Strict, Lax) = (1, 2)
    (Standard, Wolf, TheMan) = (1, 2, 3)
    TomorrowChecking = Strict
    LogfileCompletionChecking = Strict
    PreferredBulletChar = '*'
    ScheduleMode = Standard


def get_next_day(date):
    """ Given a date, return the next day by consulting the python date module """
    next_day = date + datetime.timedelta(days=1)
    return next_day


def quarter_for_month(month):
    if month.lower() in ('january', 'february', 'march'):
        return "Q1"
    elif month.lower() in ('april', 'may', 'june'):
        return "Q2"
    elif month.lower() in ('july', 'august', 'september'):
        return "Q3"
    elif month.lower() in ('october', 'november', 'december'):
        return "Q4"


def reset_heads_on_planner_files(planner):
    planner.tasklistfile.seek(0)
    planner.daythemesfile.seek(0)
    planner.dayfile.seek(0)
    planner.weekfile.seek(0)
    planner.monthfile.seek(0)
    planner.quarterfile.seek(0)
    planner.yearfile.seek(0)
    planner.checkpoints_year_file.seek(0)
    planner.periodic_year_file.seek(0)
    planner.checkpoints_quarter_file.seek(0)
    planner.periodic_quarter_file.seek(0)
    planner.checkpoints_month_file.seek(0)
    planner.periodic_month_file.seek(0)
    planner.checkpoints_week_file.seek(0)
    planner.periodic_week_file.seek(0)
    planner.checkpoints_weekday_file.seek(0)
    planner.checkpoints_weekend_file.seek(0)
    planner.periodic_day_file.seek(0)

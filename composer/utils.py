import datetime


class PlannerPeriod(object):
    (Zero, Day, Week, Month, Quarter, Year) = (0, 1, 2, 3, 4, 5)


class PlannerUserSettings(object):
    WeekTheme = None


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

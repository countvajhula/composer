import datetime
import re

from ...errors import RelativeDateError
from ...timeperiod import (
    get_next_day,
    Day,
    Week,
    Month,
    Quarter,
    Year,
    month_for_quarter,
    quarter_for_month,
    get_month_name,
    get_month_number,
)

# TODO: change these to annotated regex's

# MONTH DD, YYYY (w optional space or comma or both)
dateformat1 = re.compile(r"^([^\d ]+) (\d\d?)[, ] ?(\d{4})$", re.IGNORECASE)
# DD MONTH, YYYY (w optional space or comma or both)
dateformat2 = re.compile(r"^(\d\d?) ([^\d,]+)[, ] ?(\d{4})$", re.IGNORECASE)
# MONTH DD
dateformat3 = re.compile(r"^([^\d ]+) (\d\d?)$", re.IGNORECASE)
# DD MONTH
dateformat4 = re.compile(r"^(\d\d?) ([^\d]+)$", re.IGNORECASE)
# WEEK OF MONTH DD, YYYY (w optional space or comma or both)
dateformat5 = re.compile(
    r"^WEEK OF ([^\d ]+) (\d\d?)[, ] ?(\d{4})$", re.IGNORECASE
)
# WEEK OF DD MONTH, YYYY (w optional space or comma or both)
dateformat6 = re.compile(
    r"^WEEK OF (\d\d?) ([^\d,]+)[, ] ?(\d{4})$", re.IGNORECASE
)
# WEEK OF MONTH DD
dateformat7 = re.compile(r"^WEEK OF ([^\d ]+) (\d\d?)$", re.IGNORECASE)
# WEEK OF DD MONTH
dateformat8 = re.compile(r"^WEEK OF (\d\d?) ([^\d,]+)$", re.IGNORECASE)
# MONTH YYYY (w optional space or comma or both)
dateformat9 = re.compile(r"^([^\d, ]+)[, ] ?(\d{4})$", re.IGNORECASE)
# MONTH
dateformat10 = re.compile(r"^([^\d ]+)$", re.IGNORECASE)
# MM/DD/YYYY
dateformat11 = re.compile(r"^(\d\d)/(\d\d)/(\d\d\d\d)$", re.IGNORECASE)
# MM-DD-YYYY
dateformat12 = re.compile(r"^(\d\d)-(\d\d)-(\d\d\d\d)$", re.IGNORECASE)
# TOMORROW
dateformat13 = re.compile(r"^TOMORROW$", re.IGNORECASE)
# TODO: need a function to test date boundary status and return
# monthboundary, weekboundary, or dayboundary (default)
# NEXT WEEK
dateformat14 = re.compile(r"^NEXT WEEK$", re.IGNORECASE)
# NEXT MONTH
dateformat15 = re.compile(r"^NEXT MONTH$", re.IGNORECASE)
# <DOW>
dateformat16 = re.compile(
    r"^(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY)$",
    re.IGNORECASE,
)
# <DOW> (abbrv.)
dateformat17 = re.compile(r"^(MON|TUE|WED|THU|FRI|SAT|SUN)$", re.IGNORECASE)
# QN YYYY
dateformat18 = re.compile(r"^(Q\d) (\d{4})$", re.IGNORECASE)
# NEXT YEAR
dateformat19 = re.compile(r"^NEXT YEAR$", re.IGNORECASE)
# YYYY
dateformat20 = re.compile(r"^(\d\d\d\d)$", re.IGNORECASE)
# THIS WEEKEND
dateformat21 = re.compile(r"^THIS WEEKEND$", re.IGNORECASE)
# NEXT WEEKEND
dateformat22 = re.compile(r"^NEXT WEEKEND$", re.IGNORECASE)
# NEXT QUARTER
dateformat23 = re.compile(r"^NEXT QUARTER$", re.IGNORECASE)
# QN
dateformat24 = re.compile(r"^(Q\d)$", re.IGNORECASE)
# DAY AFTER TOMORROW
dateformat25 = re.compile(r"^DAY AFTER TOMORROW$", re.IGNORECASE)


def get_appropriate_year(month, day, reference_date):
    """ For date formats where the year is unspecified, determine the
    appropriate year by ensuring that the resulting date is in the future.

    :param int month: Indicated month
    :param int day: Indicated day
    :param :class:`datetime.date` reference_date: Date to be treated as "today"
    :returns int: The appropriate year for the date
    """
    # if current year would result in negative, then use next year,
    # otherwise current year
    date_thisyear = datetime.date(reference_date.year, month, day)
    if date_thisyear < reference_date:
        return reference_date.year + 1
    else:
        return reference_date.year


def parse_dateformat1(date_string, reference_date=None):
    (month, day, year) = dateformat1.search(date_string).groups()
    date = datetime.datetime.strptime(
        month + "-" + day + "-" + year, "%B-%d-%Y"
    ).date()
    period = Day
    return date, period


def parse_dateformat2(date_string, reference_date=None):
    (day, month, year) = dateformat2.search(date_string).groups()
    date = datetime.datetime.strptime(
        month + "-" + day + "-" + year, "%B-%d-%Y"
    ).date()
    period = Day
    return date, period


def parse_dateformat3(date_string, reference_date=None):
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    (month, day) = dateformat3.search(date_string).groups()
    (monthn, dayn) = (get_month_number(month), int(day))
    year = str(get_appropriate_year(monthn, dayn, reference_date))
    date = datetime.datetime.strptime(
        month + "-" + day + "-" + year, "%B-%d-%Y"
    ).date()
    period = Day
    return date, period


def parse_dateformat4(date_string, reference_date=None):
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    (day, month) = dateformat4.search(date_string).groups()
    (monthn, dayn) = (get_month_number(month), int(day))
    year = str(get_appropriate_year(monthn, dayn, reference_date))
    date = datetime.datetime.strptime(
        month + "-" + day + "-" + year, "%B-%d-%Y"
    ).date()
    period = Day
    return date, period


def parse_dateformat5(date_string, reference_date=None):
    # std = Week of Month dd(sunday/1), yyyy
    (month, day, year) = dateformat5.search(date_string).groups()
    (monthn, dayn, yearn) = (get_month_number(month), int(day), int(year))
    date = datetime.date(yearn, monthn, dayn)
    date = Week.get_start_date(date)
    period = Week
    return date, period


def parse_dateformat6(date_string, reference_date=None):
    (day, month, year) = dateformat6.search(date_string).groups()
    (monthn, dayn, yearn) = (get_month_number(month), int(day), int(year))
    date = datetime.date(yearn, monthn, dayn)
    date = Week.get_start_date(date)
    period = Week
    return date, period


def parse_dateformat7(date_string, reference_date=None):
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    (month, day) = dateformat7.search(date_string).groups()
    (monthn, dayn) = (get_month_number(month), int(day))
    yearn = get_appropriate_year(monthn, dayn, reference_date)
    date = datetime.date(yearn, monthn, dayn)
    date = Week.get_start_date(date)
    period = Week
    return date, period


def parse_dateformat8(date_string, reference_date=None):
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    (day, month) = dateformat8.search(date_string).groups()
    (monthn, dayn) = (get_month_number(month), int(day))
    yearn = get_appropriate_year(monthn, dayn, reference_date)
    date = datetime.date(yearn, monthn, dayn)
    date = Week.get_start_date(date)
    period = Week
    return date, period


def parse_dateformat9(date_string, reference_date=None):
    (month, year) = dateformat9.search(date_string).groups()
    day = str(1)
    date = datetime.datetime.strptime(
        month + "-" + day + "-" + year, "%B-%d-%Y"
    ).date()
    period = Month
    return date, period


def parse_dateformat10(date_string, reference_date=None):
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    month = dateformat10.search(date_string).groups()[0]
    (monthn, dayn) = (get_month_number(month), 1)
    (day, year) = (
        str(dayn),
        str(get_appropriate_year(monthn, dayn, reference_date)),
    )
    date = datetime.datetime.strptime(
        month + "-" + day + "-" + year, "%B-%d-%Y"
    ).date()
    period = Month
    return date, period


def parse_dateformat11(date_string, reference_date=None):
    (monthn, dayn, yearn) = map(int, dateformat11.search(date_string).groups())
    date = datetime.date(yearn, monthn, dayn)
    period = Day
    return date, period


def parse_dateformat12(date_string, reference_date=None):
    (monthn, dayn, yearn) = map(int, dateformat12.search(date_string).groups())
    date = datetime.date(yearn, monthn, dayn)
    period = Day
    return date, period


def parse_dateformat13(date_string, reference_date=None):
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    date = get_next_day(reference_date)
    period = Day
    return date, period


def parse_dateformat14(date_string, reference_date=None):
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    date = Week.get_end_date(reference_date) + datetime.timedelta(days=1)
    period = Week
    return date, period


def parse_dateformat15(date_string, reference_date=None):
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    date = Month.get_end_date(reference_date) + datetime.timedelta(days=1)
    period = Month
    return date, period


def parse_dateformat16(date_string, reference_date=None):
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    dowToSchedule = dateformat16.search(date_string).groups()[0]
    upcomingweek = [
        reference_date + datetime.timedelta(days=d) for d in range(1, 8)
    ]
    dow = [d.strftime("%A").upper() for d in upcomingweek]
    date = upcomingweek[dow.index(dowToSchedule)]
    period = Day
    return date, period


def parse_dateformat17(date_string, reference_date=None):
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    dowToSchedule = dateformat17.search(date_string).groups()[0]
    upcomingweek = [
        reference_date + datetime.timedelta(days=d) for d in range(1, 8)
    ]
    dow = [d.strftime("%a").upper() for d in upcomingweek]
    date = upcomingweek[dow.index(dowToSchedule)]
    period = Day
    return date, period


def parse_dateformat18(date_string, reference_date=None):
    (quarter, year) = dateformat18.search(date_string).groups()
    month = month_for_quarter(quarter)
    month = get_month_name(month)
    day = str(1)
    date = datetime.datetime.strptime(
        month + "-" + day + "-" + year, "%B-%d-%Y"
    ).date()
    period = Quarter
    return date, period


def parse_dateformat19(date_string, reference_date=None):
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    date = Year.get_end_date(reference_date) + datetime.timedelta(days=1)
    period = Year
    return date, period


def parse_dateformat20(date_string, reference_date=None):
    year = int(dateformat20.search(date_string).groups()[0])
    date = datetime.date(year, 1, 1)
    period = Year
    return date, period


def parse_dateformat21(date_string, reference_date=None):
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    date = Week.get_end_date(reference_date)
    period = Day
    return date, period


def parse_dateformat22(date_string, reference_date=None):
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    start_of_next_week = Week.get_end_date(
        reference_date
    ) + datetime.timedelta(days=1)
    date = Week.get_end_date(start_of_next_week)
    period = Day
    return date, period


def parse_dateformat23(date_string, reference_date=None):
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    date = Quarter.get_end_date(reference_date) + datetime.timedelta(days=1)
    period = Quarter
    return date, period


def parse_dateformat24(date_string, reference_date=None):
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    quarter = dateformat24.search(date_string).groups()[0]
    # start date of next quarter
    date = Quarter.get_end_date(reference_date) + datetime.timedelta(days=1)
    next_quarter = quarter_for_month(date.month)
    # find the specified quarter
    while next_quarter != quarter:
        date = Quarter.get_end_date(date) + datetime.timedelta(days=1)
        next_quarter = quarter_for_month(date.month)
    period = Quarter
    return date, period


def parse_dateformat25(date_string, reference_date=None):
    if not reference_date:
        raise RelativeDateError(
            "Relative date found, but no context available"
        )
    date = get_next_day(get_next_day(reference_date))
    period = Day
    return date, period

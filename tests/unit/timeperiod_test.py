import datetime
import pytest

from composer.timeperiod import (
    Day,
    Week,
    Month,
    Quarter,
    Year,
    Zero,
    Eternity,
    get_time_periods,
    quarter_for_month,
    month_for_quarter,
)


class TestStartDate(object):
    pass


class TestEndDate(object):
    pass


class TestDayStartDate(TestStartDate):
    def test_start_date(self):
        current_date = datetime.date(2013, 5, 15)
        expected = current_date
        result = Day.get_start_date(current_date)
        assert result == expected


class TestDayEndDate(TestEndDate):
    def test_end_date(self):
        current_date = datetime.date(2013, 5, 15)
        expected = current_date
        result = Day.get_end_date(current_date)
        assert result == expected


class TestWeekStartDate(TestStartDate):
    def test_start_date_middle_of_the_month(self):
        current_date = datetime.date(2013, 5, 15)
        expected = datetime.date(2013, 5, 12)
        result = Week.get_start_date(current_date)
        assert result == expected

    def test_current_date_is_start_date(self):
        current_date = datetime.date(2013, 5, 12)
        expected = current_date
        result = Week.get_start_date(current_date)
        assert result == expected

    def test_beginning_of_month(self):
        current_date = datetime.date(2013, 5, 3)  # Friday
        expected = datetime.date(
            2013, 5, 1
        )  # 1st of month, not Sunday (short week)
        result = Week.get_start_date(current_date)
        assert result == expected

    def test_end_of_month(self):
        current_date = datetime.date(2013, 4, 29)  # Tue
        expected = datetime.date(2013, 4, 21)  # long week
        result = Week.get_start_date(current_date)
        assert result == expected


class TestWeekEndDate(TestEndDate):
    def test_end_date_middle_of_the_month(self):
        current_date = datetime.date(2013, 5, 15)  # Wed
        expected = datetime.date(2013, 5, 18)  # Sat
        result = Week.get_end_date(current_date)
        assert result == expected

    def test_current_date_is_end_date(self):
        current_date = datetime.date(2013, 5, 18)
        expected = current_date
        result = Week.get_end_date(current_date)
        assert result == expected

    def test_beginning_of_month(self):
        current_date = datetime.date(2013, 8, 2)  # Friday
        expected = datetime.date(2013, 8, 10)  # long week
        result = Week.get_end_date(current_date)
        assert result == expected

    def test_end_of_month(self):
        current_date = datetime.date(2013, 2, 25)  # Mon
        expected = datetime.date(2013, 2, 28)  # short week
        result = Week.get_end_date(current_date)
        assert result == expected


class TestMonthStartDate(TestStartDate):
    def test_start_date_middle_of_the_month(self):
        current_date = datetime.date(2013, 5, 15)
        expected = datetime.date(2013, 5, 1)
        result = Month.get_start_date(current_date)
        assert result == expected

    def test_current_date_is_start_date(self):
        current_date = datetime.date(2013, 5, 1)
        expected = current_date
        result = Month.get_start_date(current_date)
        assert result == expected

    def test_end_of_month(self):
        current_date = datetime.date(2013, 4, 30)
        expected = datetime.date(2013, 4, 1)
        result = Month.get_start_date(current_date)
        assert result == expected


class TestMonthEndDate(TestEndDate):
    def test_end_date_middle_of_the_month(self):
        current_date = datetime.date(2013, 5, 15)
        expected = datetime.date(2013, 5, 31)
        result = Month.get_end_date(current_date)
        assert result == expected

    def test_current_date_is_end_date(self):
        current_date = datetime.date(2013, 5, 31)
        expected = current_date
        result = Month.get_end_date(current_date)
        assert result == expected

    def test_beginning_of_month(self):
        current_date = datetime.date(2013, 2, 1)
        expected = datetime.date(2013, 2, 28)
        result = Month.get_end_date(current_date)
        assert result == expected


class TestQuarterStartDate(TestStartDate):
    def test_start_date_middle_of_the_quarter(self):
        current_date = datetime.date(2013, 5, 21)
        expected = datetime.date(2013, 4, 1)
        result = Quarter.get_start_date(current_date)
        assert result == expected

    def test_current_date_is_start_date(self):
        current_date = datetime.date(2013, 4, 1)
        expected = current_date
        result = Quarter.get_start_date(current_date)
        assert result == expected

    def test_end_of_quarter(self):
        current_date = datetime.date(2013, 6, 30)
        expected = datetime.date(2013, 4, 1)
        result = Quarter.get_start_date(current_date)
        assert result == expected


class TestQuarterEndDate(TestEndDate):
    def test_end_date_middle_of_the_quarter(self):
        current_date = datetime.date(2013, 5, 21)
        expected = datetime.date(2013, 6, 30)
        result = Quarter.get_end_date(current_date)
        assert result == expected

    def test_current_date_is_end_date(self):
        current_date = datetime.date(2013, 6, 30)
        expected = current_date
        result = Quarter.get_end_date(current_date)
        assert result == expected

    def test_beginning_of_quarter(self):
        current_date = datetime.date(2013, 4, 1)
        expected = datetime.date(2013, 6, 30)
        result = Quarter.get_end_date(current_date)
        assert result == expected


class TestYearStartDate(TestStartDate):
    def test_start_date_middle_of_the_year(self):
        current_date = datetime.date(2013, 5, 21)
        expected = datetime.date(2013, 1, 1)
        result = Year.get_start_date(current_date)
        assert result == expected

    def test_current_date_is_start_date(self):
        current_date = datetime.date(2013, 1, 1)
        expected = current_date
        result = Year.get_start_date(current_date)
        assert result == expected

    def test_end_of_year(self):
        current_date = datetime.date(2013, 12, 31)
        expected = datetime.date(2013, 1, 1)
        result = Year.get_start_date(current_date)
        assert result == expected


class TestYearEndDate(TestEndDate):
    def test_end_date_middle_of_the_year(self):
        current_date = datetime.date(2013, 5, 21)
        expected = datetime.date(2013, 12, 31)
        result = Year.get_end_date(current_date)
        assert result == expected

    def test_current_date_is_end_date(self):
        current_date = datetime.date(2013, 12, 31)
        expected = current_date
        result = Year.get_end_date(current_date)
        assert result == expected

    def test_beginning_of_year(self):
        current_date = datetime.date(2013, 1, 1)
        expected = datetime.date(2013, 12, 31)
        result = Year.get_end_date(current_date)
        assert result == expected


class TestGetTimePeriods(object):
    _time_periods = (Zero, Day, Week, Month, Quarter, Year, Eternity)

    def test_get_time_periods(self):
        result = get_time_periods()
        assert result == self._time_periods

    def test_starting_from(self):
        result = get_time_periods(starting_from=Week)
        assert result == self._time_periods[2:]

    def test_decreasing(self):
        result = get_time_periods(decreasing=True)
        assert result == tuple(reversed(self._time_periods))


class TestMonthForQuarter(object):
    def test_q1(self):
        result = month_for_quarter('Q1')
        expected = 1
        assert result == expected

    def test_q2(self):
        result = month_for_quarter('Q2')
        expected = 4
        assert result == expected

    def test_q3(self):
        result = month_for_quarter('Q3')
        expected = 7
        assert result == expected

    def test_q4(self):
        result = month_for_quarter('Q4')
        expected = 10
        assert result == expected


class TestQuarterForMonth(object):
    @pytest.mark.parametrize(
        "date",
        [
            datetime.date(2012, 1, 12),
            datetime.date(2012, 2, 12),
            datetime.date(2012, 3, 12),
        ],
    )
    def test_q1(self, date):
        result = quarter_for_month(date.month)
        expected = 'Q1'
        assert result == expected

    @pytest.mark.parametrize(
        "date",
        [
            datetime.date(2012, 4, 12),
            datetime.date(2012, 5, 12),
            datetime.date(2012, 6, 12),
        ],
    )
    def test_q2(self, date):
        date = datetime.date(2012, 4, 12)
        result = quarter_for_month(date.month)
        expected = 'Q2'
        assert result == expected

    @pytest.mark.parametrize(
        "date",
        [
            datetime.date(2012, 7, 12),
            datetime.date(2012, 8, 12),
            datetime.date(2012, 9, 12),
        ],
    )
    def test_q3(self, date):
        date = datetime.date(2012, 7, 12)
        result = quarter_for_month(date.month)
        expected = 'Q3'
        assert result == expected

    @pytest.mark.parametrize(
        "date",
        [
            datetime.date(2012, 10, 12),
            datetime.date(2012, 11, 12),
            datetime.date(2012, 12, 12),
        ],
    )
    def test_q4(self, date):
        date = datetime.date(2012, 10, 12)
        result = quarter_for_month(date.month)
        expected = 'Q4'
        assert result == expected


class TestMonthToQuarterSanity(object):
    @pytest.mark.parametrize(
        "date, expected",
        [
            (datetime.date(2012, 1, 12), 'Q1'),
            (datetime.date(2012, 2, 12), 'Q1'),
            (datetime.date(2012, 3, 12), 'Q1'),
            (datetime.date(2012, 4, 12), 'Q2'),
            (datetime.date(2012, 5, 12), 'Q2'),
            (datetime.date(2012, 6, 12), 'Q2'),
            (datetime.date(2012, 7, 12), 'Q3'),
            (datetime.date(2012, 8, 12), 'Q3'),
            (datetime.date(2012, 9, 12), 'Q3'),
            (datetime.date(2012, 10, 12), 'Q4'),
            (datetime.date(2012, 11, 12), 'Q4'),
            (datetime.date(2012, 12, 12), 'Q4'),
        ],
    )
    def test_quarter_month_quarter(self, date, expected):
        result = quarter_for_month(
            month_for_quarter(quarter_for_month(date.month))
        )
        assert result == expected

    @pytest.mark.parametrize(
        "quarter, expected", [('Q1', 1), ('Q2', 4), ('Q3', 7), ('Q4', 10)]
    )
    def test_month_quarter_month(self, quarter, expected):
        result = month_for_quarter(
            quarter_for_month(month_for_quarter(quarter))
        )
        assert result == expected

import datetime

from composer.timeperiod import (
    Day, Week, Month, Quarter, Year,
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
        expected = datetime.date(2013, 5, 1)  # 1st of month, not Sunday (short week)
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

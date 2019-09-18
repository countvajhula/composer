import datetime

from composer.timeperiod import (
    Week,
)


class TestWeekStartDate(object):
    def test_start_date_middle_of_the_month(self):
        current_date = datetime.date(2013, 5, 15)  # Wed
        expected = datetime.date(2013, 5, 12)  # Sun
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


class TestWeekEndDate(object):
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

import pytest
from datetime import date, timedelta
from mock import patch

from composer.backend.filesystem.interface import (
    get_constituent_logs,
    time_spent_on_planner,
)
from composer.timeperiod import Day, Week

try:  # py2
    from StringIO import StringIO
except ImportError:  # py3
    from io import StringIO


try:  # py3
    FileNotFoundError
except NameError:  # py2
    FileNotFoundError = IOError


class LogTimes(object):

    times = 0

    def __init__(self, n):
        self.n = n

    def __call__(self, *args, **kwargs):
        if self.times < self.n:
            self.times += 1
            return str(self.times)
        raise FileNotFoundError


class TestTimeSpentOnPlanner(object):
    @pytest.mark.parametrize(
        "time_string, expected_time",
        [
            ('10 mins\n', 10),
            ('1hr 55mins\n', 115),
            ('1 hr 55 mins\n', 115),
            ('2 hr 10 min\n', 130),
            ('2hrs 10min\n', 130),
            ('35 + 10 = 45 mins\n', 45),
            ('35 + 30 = 1hr 5 mins\n', 65),
            ('5 mins (completed next day)\n', 5),
            ('1hr 5 mins (completed next day)\n', 65),
            ('35 + 30 = 1hr 5 mins (completed next day)\n', 65),
        ],
    )
    @patch('composer.backend.filesystem.interface.read_section')
    @patch('composer.backend.filesystem.interface.read_file')
    def test_time_is_parsed(
        self, mock_read_file, mock_read_section, time_string, expected_time
    ):
        mock_read_file.return_value = StringIO('')
        mock_read_section.return_value = StringIO(time_string), StringIO('')
        for_date = date.today() - timedelta(days=15)
        time_spent = time_spent_on_planner(Day, for_date, '/path/to/root')
        assert time_spent == expected_time


class TestGetConstituentLogs(object):
    @patch('composer.backend.filesystem.interface.get_log_for_date')
    def test_for_day_returns_empty(self, mock_get_log):
        mock_get_log.side_effect = LogTimes(1)
        for_date = date.today() - timedelta(days=15)
        logs = get_constituent_logs(Day, for_date, '/path/to/root')
        assert logs == []

    @patch('composer.backend.filesystem.interface.get_log_for_date')
    def test_for_in_progress_period(self, mock_get_log):
        mock_get_log.side_effect = LogTimes(1)
        for_date = date.today() - timedelta(days=15)
        logs = get_constituent_logs(Week, for_date, '/path/to/root')
        assert logs == ['1']

    @patch('composer.backend.filesystem.interface.get_log_for_date')
    def test_for_completed_period(self, mock_get_log):
        mock_get_log.side_effect = LogTimes(10)
        for_date = date(2012, 10, 16)
        logs = get_constituent_logs(Week, for_date, '/path/to/root')
        assert logs == [str(i) for i in range(1, 8)]

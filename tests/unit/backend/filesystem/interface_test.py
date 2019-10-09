from datetime import date, timedelta
from mock import patch

from composer.backend.filesystem.interface import get_constituent_logs
from composer.timeperiod import Day, Week

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

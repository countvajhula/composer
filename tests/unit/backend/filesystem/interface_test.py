import pytest
from datetime import date, timedelta
from mock import patch

from composer.backend.filesystem.interface import (
    get_log_for_date,
    get_constituent_logs,
    compute_time_spent_on_planner,
    time_spent_on_planner,
)
from composer.timeperiod import Zero, Day, Week
from ...fixtures import logfile, complete_logfile  # noqa

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


class TestGetLogForDate(object):
    @patch('composer.backend.filesystem.interface.read_file')
    def test_retrieves_log(self, mock_read_file, logfile):
        mock_read_file.return_value = logfile
        for_date = date.today() - timedelta(days=15)
        log = get_log_for_date(Day, for_date, '/path/to/root')
        assert log == logfile


# TODO: better to test string_to_time for the various formats
# and have a simple integration test for time_spent_on_planner
class TestTimeSpentOnPlanner(object):
    @pytest.mark.parametrize(
        "time_string, expected_time",
        [
            ('10 mins\n', 10),
            ('1 hr\n', 60),
            ('1hr 55mins\n', 115),
            ('1 hr 55 mins\n', 115),
            ('2 hr 10 min\n', 130),
            ('2hrs 10min\n', 130),
            ('35 + 10 = 45 mins\n', 45),
            ('1hr + 1hr = 2hrs\n', 120),
            ('35 + 30 = 1hr 5 mins\n', 65),
            ('35? + 10 = 45 mins\n', 45),
            ('35 + 10? = 45 mins\n', 45),
            ('2 hrs + 10 mins = 2hr 10mins', 130),
            ('5 mins (completed next day)\n', 5),
            ('3 hrs (completed next day)\n', 180),
            ('1hr 5 mins (completed next day)\n', 65),
            ('35 + 30 = 1hr 5 mins (completed next day)\n', 65),
        ],
    )
    @patch('composer.backend.filesystem.interface.get_entries')
    @patch('composer.backend.filesystem.interface.read_file')
    def test_time_is_parsed(
        self,
        mock_read_file,
        mock_get_entries,
        time_string,
        expected_time,
        logfile,
    ):
        mock_read_file.return_value = StringIO('')
        mock_get_entries.return_value = [
            'TIME SPENT ON PLANNER: ' + time_string
        ]
        time_spent = time_spent_on_planner(logfile)
        assert time_spent == expected_time

    @patch('composer.backend.filesystem.interface.get_entries')
    @patch('composer.backend.filesystem.interface.read_file')
    def test_missing_time(
        self,
        mock_read_file,
        mock_get_entries,
        logfile,
    ):
        mock_read_file.return_value = StringIO('')
        mock_get_entries.return_value = ['TIME SPENT ON PLANNER: ']
        time_spent = time_spent_on_planner(logfile)
        assert time_spent == 0


class TestComputeTimeSpentOnPlanner(object):
    def test_no_time_is_spent_on_zero_period(
        self,
    ):
        for_date = date.today() - timedelta(days=15)
        time_spent = compute_time_spent_on_planner(
            Zero, for_date, '/path/to/root'
        )
        assert time_spent == (0, 0)

    @patch('composer.backend.filesystem.interface.get_log_for_date')
    def test_time_spent_on_day(self, mock_get_log, complete_logfile):
        mock_get_log.return_value = complete_logfile
        for_date = date.today() - timedelta(days=15)
        time_spent = compute_time_spent_on_planner(
            Day, for_date, '/path/to/root'
        )
        assert time_spent == (0, 25)

    @patch('composer.backend.filesystem.interface.get_constituent_logs')
    def test_time_spent_on_week(self, mock_get_logs, complete_logfile):
        mock_get_logs.return_value = [
            complete_logfile,
            complete_logfile,
            complete_logfile,
        ]
        for_date = date.today() - timedelta(days=15)
        time_spent = compute_time_spent_on_planner(
            Week, for_date, '/path/to/root'
        )
        assert time_spent == (1, 15)


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

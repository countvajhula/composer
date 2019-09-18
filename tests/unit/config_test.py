import pytest

from composer.config import read_user_preferences
from composer.errors import ConfigError

from .fixtures import config_file

from mock import patch

try:  # py3
    import configparser
except ImportError:  # py2
    import ConfigParser as configparser


class TestReadUserPreferences(object):
    @patch('composer.config.os.path.isfile', return_value=False)
    def test_file_missing_raises_error(self, mock_isfile):
        with pytest.raises(ConfigError):
            read_user_preferences('/dummy/path/to/file.ini')

    @patch('composer.config._read_config')
    @patch('composer.config.os.path.isfile', return_value=True)
    def test_read_user_preferences(self, mock_isfile, mock_read_config, config_file):
        cfg = configparser.ConfigParser()
        cfg.read_file(config_file)
        mock_read_config.return_value = cfg
        expected = {
            "wikis": [
                "/Users/siddhartha/log/themanwiki",
                "/Users/siddhartha/log/ferdywiki",
                "/Users/siddhartha/log/planner",
            ],
            "lessons_files": [
                "Lessons_Introspective.wiki",
                "Lessons_General.wiki",
                "Lessons_Advice.wiki",
                "Lessons_Experimental.wiki",
            ],
            "schedule": "standard",
            "bullet_character": "*",
        }
        result = read_user_preferences('/dummy/path')
        assert result == expected

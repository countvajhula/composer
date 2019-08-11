import csv

try:  # py3
    import configparser
except ImportError:  # py2
    import ConfigParser as configparser

LOGFILE_CHECKING = {
    'STRICT': 1,
    'LAX': 2,
}

DEFAULT_SCHEDULE = 'standard'
DEFAULT_BULLET_CHARACTER = '*'


def read_user_preferences(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    preferences = dict(config['general'])
    # convert from string to list
    preferences['wikis'] = next(csv.reader([preferences['wikis']]))
    preferences['lessons_files'] = next(csv.reader([preferences['lessons_files']]))
    return preferences

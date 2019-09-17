import csv
import os

from .errors import ConfigError

try:  # py3
    import configparser
except ImportError:  # py2
    import ConfigParser as configparser

CONFIG_FILENAME = "config.ini"

LOGFILE_CHECKING = {"STRICT": 1, "LAX": 2}

DEFAULT_SCHEDULE = "standard"
DEFAULT_BULLET_CHARACTER = "*"


def read_user_preferences(config_path):
    """ Read composer config including wiki paths.

    :param str config_path: The location of the config file
    :returns dict: A dictionary corresponding to the user's preferences
        as indicated in the config file.
    """
    if not os.path.isfile(config_path):
        raise ConfigError(
            "Composer config file at {path} missing!".format(path=config_path)
        )
    config = configparser.ConfigParser()
    config.read(config_path)
    preferences = dict(config["general"])
    # convert from string to list
    preferences["wikis"] = next(csv.reader([preferences["wikis"]]))
    preferences["lessons_files"] = next(
        csv.reader([preferences["lessons_files"]])
    )
    return preferences


def update_wiki_specific_preferences(wikidir, preferences):
    """ Read wiki-specific config, if present.

    This mutates the preferences dictionary, overriding any default config
    read previously where there is overlap.

    :param str wikidir: The location of the wiki
    """
    config_path = os.path.join(wikidir, CONFIG_FILENAME)
    if not os.path.isfile(config_path):
        return
    config = configparser.ConfigParser()
    config.read(config_path)
    wiki_preferences = dict(config["general"])
    # convert from string to list
    wiki_preferences["lessons_files"] = next(
        csv.reader([preferences["lessons_files"]])
    )
    # override lessons files, schedule, preferred bullet char, and
    # anything else
    preferences.update(wiki_preferences)

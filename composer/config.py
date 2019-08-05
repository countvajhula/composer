import configparser
import csv

LOGFILE_CHECKING = {
    'STRICT': 1,
    'LAX': 2,
}

DEFAULT_SCHEDULE = 'standard'
DEFAULT_BULLET_CHARACTER = '*'


class PlannerConfig(object):
    TomorrowChecking = LOGFILE_CHECKING['STRICT']
    LogfileCompletionChecking = LOGFILE_CHECKING['STRICT']
    PreferredBulletChar = DEFAULT_BULLET_CHARACTER
    Schedule = DEFAULT_SCHEDULE


def read_user_preferences(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    preferences = dict(config['general'])
    # convert from string to list
    preferences['wikis'] = next(csv.reader([preferences['wikis']]))
    preferences['lessons_files'] = next(csv.reader([preferences['lessons_files']]))
    return preferences


def set_preferences(preferences=None, jump=False):
    PlannerConfig.Schedule = (preferences['schedule']
                              if preferences
                              else DEFAULT_SCHEDULE)
    PlannerConfig.PreferredBulletChar = (preferences['bullet_character']
                                         if preferences
                                         else DEFAULT_BULLET_CHARACTER)
    PlannerConfig.LogfileCompletionChecking = (LOGFILE_CHECKING['LAX']
                                               if jump
                                               else LOGFILE_CHECKING['STRICT'])
    PlannerConfig.TomorrowChecking = (LOGFILE_CHECKING['LAX']
                                      if jump
                                      else LOGFILE_CHECKING['STRICT'])

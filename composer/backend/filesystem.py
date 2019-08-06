from .base import PlannerBase


class FilesystemPlanner(PlannerBase):
    tasklistfile = None
    daythemesfile = None
    dayfile = None
    weekfile = None
    monthfile = None
    quarterfile = None
    yearfile = None
    checkpoints_weekday_file = None
    checkpoints_weekend_file = None
    checkpoints_week_file = None
    checkpoints_month_file = None
    checkpoints_quarter_file = None
    checkpoints_year_file = None
    periodic_day_file = None
    periodic_week_file = None
    periodic_month_file = None
    periodic_quarter_file = None
    periodic_year_file = None

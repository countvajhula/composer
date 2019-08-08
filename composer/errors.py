class ComposerError(Exception):
    """  Base error class for composer errors. """
    pass


class DayStillInProgressError(ComposerError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class PlannerIsInTheFutureError(ComposerError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class TomorrowIsEmptyError(ComposerError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class LogfileNotCompletedError(ComposerError):
    def __init__(self, value, period):
        self.value = value
        self.period = period

    def __str__(self):
        return repr(self.value)


class PlannerStateError(ComposerError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SimulationPassedError(ComposerError):
    def __init__(self, value, status):
        self.value = value
        self.status = status

    def __str__(self):
        return repr(self.value)

# LAYOUT ERRORS


class LayoutError(ComposerError):
    """  Base error class for file layout errors. """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class TasklistLayoutError(LayoutError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class LogfileLayoutError(LayoutError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

# SCHEDULING ERRORS


class SchedulingError(ComposerError):
    """  Base error class for scheduling errors. """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BlockedTaskNotScheduledError(SchedulingError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SchedulingDateError(SchedulingError):
    """  Base error class for date-related errors in scheduling. """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DateFormatError(SchedulingDateError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class RelativeDateError(SchedulingDateError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

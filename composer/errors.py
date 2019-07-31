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


class DateFormatError(ComposerError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BlockedTaskNotScheduledError(ComposerError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class PlannerStateError(ComposerError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class RelativeDateError(ComposerError):
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


class LayoutError(ComposerError):
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

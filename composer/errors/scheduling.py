from . import ComposerError


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


class ScheduledTaskParsingError(SchedulingError):
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


class InvalidDateError(SchedulingDateError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

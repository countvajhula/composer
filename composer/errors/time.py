from . import ComposerError


class TimeError(ComposerError):
    """Base error class for time-related errors."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InvalidTimeFormatError(TimeError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

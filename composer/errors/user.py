from . import ComposerError


class UserError(ComposerError):
    """  Base error class for user-related errors. """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class TomorrowIsEmptyError(UserError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class LogfileNotCompletedError(UserError):
    def __init__(self, value, period):
        self.value = value
        self.period = period

    def __str__(self):
        return repr(self.value)

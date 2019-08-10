from . import ComposerError


class PlannerStateError(ComposerError):
    """  Base error class for planner state errors. """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DayStillInProgressError(PlannerStateError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class PlannerIsInTheFutureError(PlannerStateError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class LogfileAlreadyExistsError(PlannerStateError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

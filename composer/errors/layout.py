from . import ComposerError


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

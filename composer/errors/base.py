class ComposerError(Exception):
    """  Base error class for composer errors. """

    pass


class SimulationPassedError(ComposerError):
    def __init__(self, value, status):
        self.value = value
        self.status = status

    def __str__(self):
        return repr(self.value)

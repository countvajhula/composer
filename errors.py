class DayStillInProgressError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)


class PlannerIsInTheFutureError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)


class TomorrowIsEmptyError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)


class LogfileNotCompletedError(Exception):
	def __init__(self, value, period):
		self.value = value
		self.period = period

	def __str__(self):
		return repr(self.value)


class DateFormatError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)


class BlockedTaskNotScheduledError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)


class TasklistLayoutError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)


class LogfileLayoutError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)


class PlannerStateError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)


class RelativeDateError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)


class SimulationPassedError(Exception):
	def __init__(self, value, status):
		self.value = value
		self.status = status

	def __str__(self):
		return repr(self.value)

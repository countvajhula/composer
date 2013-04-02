
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
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class DayLogfileNotCompletedError(LogfileNotCompletedError):
	def __init__(self, value):
		super(DayLogfileNotCompletedError, self).__init__(value)
		self.type = 'day'

class WeekLogfileNotCompletedError(LogfileNotCompletedError):
	def __init__(self, value):
		super(WeekLogfileNotCompletedError, self).__init__(value)
		self.type = 'week'

class MonthLogfileNotCompletedError(LogfileNotCompletedError):
	def __init__(self, value):
		super(MonthLogfileNotCompletedError, self).__init__(value)
		self.type = 'month'

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


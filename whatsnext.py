#!/usr/bin/env python

from advanceplanner import *

WIKIDIR = 'tests/testwikis/userwiki'
#WIKIDIR = '/Users/siddhartha/log/planner'

if __name__ == '__main__':
	#Moved pending tasks from today over to tomorrow's agenda
	#could try: [Display score for today]
	while True:
		try:
			advanceFilesystemPlanner(WIKIDIR)
			break
		except DayStillInProgressError as err:
			print "Current day is still in progress! Try again after 6pm."
			break
		except PlannerIsInTheFutureError as err:
			raise
		except TomorrowIsEmptyError as err:
			yn = raw_input("The tomorrow section is blank. Do you want to add some tasks for tomorrow?")
			if yn.lower().startswith('y'):
				raw_input('No problem. Press any key when you are done adding tasks...')
			elif yn.lower().startswith('n'):
				PlannerConfig.TomorrowChecking = PlannerConfig.Lax
			else:
				continue
		except LogfileNotCompletedError as err:
			yn = raw_input("Looks like you haven't completed your logfile (e.g. DAILYs and NOTES). Would you like to do that now?")
			if yn.lower().startswith('y'):
				raw_input('No problem. Press any key when you are done completing your log...')
			elif yn.lower().startswith('n'):
				PlannerConfig.LogfileCompletionChecking = PlannerConfig.Lax
			else:
				continue
		except DateFormatError as err:
			raise
		except BlockedTaskNotScheduledError as err:
			raise
		except TasklistLayoutError as err:
			raise
		except LogfileLayoutError as err:
			raise
		except PlannerStateError as err:
			raise


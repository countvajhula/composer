#!/usr/bin/env python

from advanceplanner import *

WIKIDIR = 'tests/testwikis/userwiki'
#WIKIDIR = '/Users/siddhartha/log/planner'

if __name__ == '__main__':
	#Moved pending tasks from today over to tomorrow's agenda
	#could try: [Display score for today]

	# simulate the changes first and then when it's all OK, make the necessary
	# preparations (e.g. git commit) and actually perform the changes
	simulate = True 
	while True:
		try:
			advanceFilesystemPlanner(WIKIDIR, now=None, simulate=simulate)
			break
		except SimulationPassedError as err:
			# TODO: git stuff
			#print "DEV: simulation passed. let's do this thing ... for real."
			simulate = False
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
			yn = raw_input("Looks like you haven't completed your %s's log (e.g. NOTES). Would you like to do that now?" % err.type)
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


#!/usr/bin/env python

from advanceplanner import *
import updateindex
from subprocess import call

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
			print
			print "Moving tasks added for tomorrow over to tomorrow's agenda..."
			print "Carrying over any unfinished tasks from today to tomorrow's agenda..."
			print "Checking for any other tasks previously scheduled for tomorrow..."
			print "Creating/updating log files..."
			print "...DONE."
			# update index after making changes
			print
			print "Updating planner wiki index..."
			updateindex.update_index(WIKIDIR)
			print "...DONE."
			# git commit "after"
			print
			print "Committing all changes..."
			plannerdate = getPlannerDate(WIKIDIR)
			(date, month, year) = (plannerdate.day, plannerdate.strftime('%B'), plannerdate.year)
			datestr = '%s %d, %d' % (month, date, year)
			with open(os.devnull, 'w') as null:
				call(['git', 'add', '-A'], cwd=WIKIDIR, stdout=null)
				call(['git', 'commit', '-m', 'SOD %s' % datestr], cwd=WIKIDIR, stdout=null)
			print "...DONE."
			print
			break
		except SimulationPassedError as err:
			#print "DEV: simulation passed. let's do this thing ... for real."
			if err.status >= AdvancePlannerStatus.WeekAdded:
				theme = raw_input("(Optional) Enter a theme for the upcoming week, e.g. Week of 'Timeliness', or 'Completion':__")
				if theme: PlannerUserSettings.WeekTheme = theme
			if err.status >= AdvancePlannerStatus.DayAdded:
				# git commit a "before", now that we know changes are about to be written to planner
				print
				print "Saving EOD planner state before making changes..."
				plannerdate = getPlannerDate(WIKIDIR)
				(date, month, year) = (plannerdate.day, plannerdate.strftime('%B'), plannerdate.year)
				datestr = '%s %d, %d' % (month, date, year)
				with open(os.devnull, 'w') as null:
					call(['git', 'add', '-A'], cwd=WIKIDIR, stdout=null)
					call(['git', 'commit', '-m', 'EOD %s' % datestr], cwd=WIKIDIR, stdout=null)
				print "...DONE."
			if err.status >= AdvancePlannerStatus.DayAdded:
				planner = constructPlannerFromFileSystem(WIKIDIR)
				dayagenda = extractAgendaFromLogfile(planner.dayfile)
				if dayagenda:
					updateLogfileAgenda(planner.weekfile, dayagenda)
				writePlannerToFilesystem(planner, WIKIDIR)
			if err.status >= AdvancePlannerStatus.WeekAdded:
				planner = constructPlannerFromFileSystem(WIKIDIR)
				weekagenda = extractAgendaFromLogfile(planner.weekfile)
				if weekagenda:
					updateLogfileAgenda(planner.monthfile, weekagenda)
				writePlannerToFilesystem(planner, WIKIDIR)
			simulate = False
		except DayStillInProgressError as err:
			print "Current day is still in progress! Try again after 6pm."
			break
		except PlannerIsInTheFutureError as err:
			raise
		except TomorrowIsEmptyError as err:
			yn = raw_input("The tomorrow section is blank. Do you want to add some tasks for tomorrow? [y/n]__")
			if yn.lower().startswith('y'):
				raw_input('No problem. Press any key when you are done adding tasks...')
			elif yn.lower().startswith('n'):
				PlannerConfig.TomorrowChecking = PlannerConfig.Lax
			else:
				continue
		except LogfileNotCompletedError as err:
			yn = raw_input("Looks like you haven't completed your %s's log (e.g. NOTES). Would you like to do that now? [y/n]__" % err.type)
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


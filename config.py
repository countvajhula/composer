import utils

def set_preferences(jumping):
	utils.PlannerConfig.ScheduleMode = utils.PlannerConfig.Wolf
	utils.PlannerConfig.PreferredBulletChar = '*'
	if jumping:
		utils.PlannerConfig.LogfileCompletionChecking = utils.PlannerConfig.Lax
		utils.PlannerConfig.TomorrowChecking = utils.PlannerConfig.Lax
	else:
		utils.PlannerConfig.LogfileCompletionChecking = utils.PlannerConfig.Strict
		utils.PlannerConfig.TomorrowChecking = utils.PlannerConfig.Strict


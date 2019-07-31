from . import utils

TEST_WIKIDIRS = ('tests/testwikis/userwiki',)
PRODUCTION_WIKIDIRS = ('/Users/siddhartha/log/themanwiki', '/Users/siddhartha/log/ferdywiki', '/Users/siddhartha/log/planner')
LESSONS_FILES = ('Lessons_Introspective.wiki', 'Lessons_General.wiki', 'Lessons_Advice.wiki', 'Lessons_Experimental.wiki')


def set_preferences(jump):
    utils.PlannerConfig.ScheduleMode = utils.PlannerConfig.TheMan  # Standard, Wolf, TheMan
    utils.PlannerConfig.PreferredBulletChar = '*'
    if jump:
        utils.PlannerConfig.LogfileCompletionChecking = utils.PlannerConfig.Lax
        utils.PlannerConfig.TomorrowChecking = utils.PlannerConfig.Lax
    else:
        utils.PlannerConfig.LogfileCompletionChecking = utils.PlannerConfig.Strict
        utils.PlannerConfig.TomorrowChecking = utils.PlannerConfig.Strict

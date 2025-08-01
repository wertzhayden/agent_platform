from rest_framework.routers import DefaultRouter
from webscraper.views.ourlads.ourlads_depth_chart import IngestOurladsDepthCharts
from webscraper.views.ourlads.player_game_and_career_stats import IngestPlayersGameAndCareerStats
from webscraper.views.two_four_seven_sports.recruits_by_school_and_year import RecruitsBySchoolAndYear
from webscraper.views.two_four_seven_sports.recruits_current_info_ourlads import IngestRecruitsCurrentData
from webscraper.views.ourlads.ourlads_nfl_active_players import IngestActiveNFLPlayersBySchool
from django.urls import path, include

router = DefaultRouter()
router.register(r'depth-charts', IngestOurladsDepthCharts, basename='depth-charts')
router.register(r'stats', IngestPlayersGameAndCareerStats, basename='stats')
router.register(r'recruits', RecruitsBySchoolAndYear, basename='recruits')
router.register(r'current-data', IngestRecruitsCurrentData, basename='recruits-current-info')
router.register(r'active-nfl-players', IngestActiveNFLPlayersBySchool, basename='active-nfl-players')

urlpatterns = [
    path('', include(router.urls)),
]

from rest_framework.routers import DefaultRouter
from webscraper.views.ourlads_depth_chart import IngestOurladsDepthCharts
from webscraper.views.player_game_and_career_stats import IngestPlayersGameAndCareerStats
from webscraper.views.recruits_by_player_and_year import RecruitsBySchoolAndYear
from webscraper.views.recruits_current_info_via_ourlads import IngestRecruitsCurrentData
from django.urls import path, include

router = DefaultRouter()
router.register(r'depth-charts', IngestOurladsDepthCharts, basename='depth-charts')
router.register(r'stats', IngestPlayersGameAndCareerStats, basename='stats')
router.register(r'recruits', RecruitsBySchoolAndYear, basename='recruits')
router.register(r'current-data', IngestRecruitsCurrentData, basename='recruits-current-info')

urlpatterns = [
    path('', include(router.urls)),
]

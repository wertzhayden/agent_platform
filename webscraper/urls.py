from rest_framework.routers import DefaultRouter
from webscraper.views import WebScrapePlayerStats
from django.urls import path, include

router = DefaultRouter()
router.register(r'items', WebScrapePlayerStats, basename='player-stats')

urlpatterns = [
    path('', include(router.urls)),
]

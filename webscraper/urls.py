from rest_framework.routers import DefaultRouter
from webscraper.views.ourlads_depth_chart import IngestOurladsDepthCharts
from django.urls import path, include

router = DefaultRouter()
router.register(r'items', IngestOurladsDepthCharts, basename='player-stats')

urlpatterns = [
    path('', include(router.urls)),
]

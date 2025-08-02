from rest_framework.routers import DefaultRouter
from django.urls import path, include

from core.views.retrieve_player import RetrievePlayersViewset
from core.views.thug_position_algorithm import ThugPositionsBySchoolViewset


router = DefaultRouter()
router.register(r'retrieve-players', RetrievePlayersViewset, basename='retrieve-players')
router.register(r'thug-positions', ThugPositionsBySchoolViewset, basename='thug-positions')

urlpatterns = [
    path('', include(router.urls)),
]

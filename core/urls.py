from rest_framework.routers import DefaultRouter
from django.urls import path, include

from core.views.retrieve_player import RetrievePlayersViewset


router = DefaultRouter()
router.register(r'retrieve-players', RetrievePlayersViewset, basename='retrieve-players')

urlpatterns = [
    path('', include(router.urls)),
]

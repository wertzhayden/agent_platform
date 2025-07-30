from rest_framework.routers import DefaultRouter

from django.urls import path, include

from accolades.views.ingest_accolade_lists import IngestAccoladesViewset
from accolades.views.expose_lists import ExposeAccoladeLists

router = DefaultRouter()
router.register(r'save-lists', IngestAccoladesViewset, basename='player-accolades')
router.register(r'expose-lists', ExposeAccoladeLists, basename='player-lists')


urlpatterns = [
    path('', include(router.urls)),
]

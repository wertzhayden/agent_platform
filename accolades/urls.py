from rest_framework.routers import DefaultRouter
from accolades.views import IngestAccoladesViewset
from django.urls import path, include

router = DefaultRouter()
router.register(r'accolades', IngestAccoladesViewset, basename='player-accolades')

urlpatterns = [
    path('', include(router.urls)),
]

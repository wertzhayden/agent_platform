from graphene_django.types import DjangoObjectType
from accolades.models.accolade import Accolade

class AccoladesType(DjangoObjectType):
    class Meta:
        model = Accolade
        fields = "__all__"
        
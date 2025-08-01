from graphene_django.types import DjangoObjectType
from webscraper.models.recruit import Recruit

class RecruitType(DjangoObjectType):
    class Meta:
        model = Recruit
        fields = "__all__"

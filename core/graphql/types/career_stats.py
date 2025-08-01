import graphene
from graphene_django.types import DjangoObjectType

from webscraper.models.career_stats.qb import QBCareerStats
from webscraper.models.career_stats.rb import RBCareerStats
from webscraper.models.career_stats.wr import ReceiverCareerStats
from webscraper.models.career_stats.defense import DefenseCareerStats

class QBCareerStatsType(DjangoObjectType):
    class Meta:
        model = QBCareerStats
        fields = "__all__"

class RBCareerStatsType(DjangoObjectType):
    class Meta:
        model = RBCareerStats
        fields = "__all__"

class ReceiverCareerStatsType(DjangoObjectType):
    class Meta:
        model = ReceiverCareerStats
        fields = "__all__"

class DefenseCareerStatsType(DjangoObjectType):
    class Meta:
        model = DefenseCareerStats
        fields = "__all__"

class CareerStatsUnion(graphene.Union):
    class Meta:
        types = (
            QBCareerStatsType,
            RBCareerStatsType,
            ReceiverCareerStatsType,
            DefenseCareerStatsType
        )

    @classmethod
    def resolve_type(cls, instance, info):
        if hasattr(instance, "completions") and hasattr(instance, "passing_yards"):
            return QBCareerStatsType
        if hasattr(instance, "attempts") and hasattr(instance, "rushing_yards"):
            return RBCareerStatsType
        if hasattr(instance, "receptions") and hasattr(instance, "receiving_yards") and hasattr(instance, "rush_attempts"):
            return ReceiverCareerStatsType
        if hasattr(instance, "sacks") and hasattr(instance, "solo_tackles"):
            return DefenseCareerStatsType
        return None
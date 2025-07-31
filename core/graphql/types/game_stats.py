import graphene
from graphene_django.types import DjangoObjectType

from webscraper.models.game_stats.qb import QBGameStats
from webscraper.models.game_stats.rb import RBGameStats
from webscraper.models.game_stats.wr import ReceiverGameStats
from webscraper.models.game_stats.defense import DefenseGameStats

class QBGameStatsType(DjangoObjectType):
    class Meta:
        model = QBGameStats
        fields = "__all__"

class RBGameStatsType(DjangoObjectType):
    class Meta:
        model = RBGameStats
        fields = "__all__"

class ReceiverGameStatsType(DjangoObjectType):
    class Meta:
        model = ReceiverGameStats
        fields = "__all__"

class DefenseGameStatsType(DjangoObjectType):
    class Meta:
        model = DefenseGameStats
        fields = "__all__"


class GameStatsUnion(graphene.Union):
    class Meta:
        types = (
            QBGameStatsType,
            RBGameStatsType,
            ReceiverGameStatsType,
            DefenseGameStatsType
        )
    
    @classmethod
    def resolve_type(cls, instance, info):
        if hasattr(instance, "completions") and hasattr(instance, "passing_yards"):
            return QBGameStatsType
        if hasattr(instance, "attempts") and hasattr(instance, "rushing_yards"):
            return RBGameStatsType
        if hasattr(instance, "receptions") and hasattr(instance, "receiving_yards") and hasattr(instance, "rush_attempts"):
            return ReceiverGameStatsType
        if hasattr(instance, "sacks") and hasattr(instance, "solo_tackles"):
            return DefenseGameStatsType
        return None
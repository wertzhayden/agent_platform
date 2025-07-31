import graphene
from graphene_django.types import DjangoObjectType
from core.models.player import Player
from core.graphql.types.career_stats import CareerStatsUnion
from core.graphql.types.game_stats import GameStatsUnion
from core.graphql.types.school import SchoolType

class PlayerType(DjangoObjectType):
    school = graphene.Field(SchoolType)
    career_stats = graphene.List(CareerStatsUnion)
    game_stats = graphene.List(GameStatsUnion)

    class Meta:
        model = Player
        fields = "__all__"

    def resolve_career_stats(self, info):
        if self.position == "QB":
            return self.qbcareerstats_career_stats.all().distinct("season")
        elif self.position == "RB":
            return self.rbcareerstats_career_stats.all().distinct("season")
        elif self.position in ["WR", "TE", "SB"]:
            return self.receivercareerstats_career_stats.all().distinct("season")
        elif self.side_of_ball == "Defense":
            return self.defensecareerstats_career_stats.all().distinct("season")
        return []

    def resolve_game_stats(self, info):
        if self.position == "QB":
            return self.qbgamestats_game_stats.all().distinct("date")
        elif self.position == "RB":
            return self.rbgamestats_game_stats.all().distinct("date")
        elif self.position in ["WR", "TE", "SB"]:
            return self.receivergamestats_game_stats.all().distinct("date")
        elif self.side_of_ball == "Defense":
            return self.defensegamestats_game_stats.all().distinct("date")
        return []
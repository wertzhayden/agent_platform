import graphene
from core.models.player import Player
from core.graphql.types.player import PlayerType

class PlayerQuery(graphene.ObjectType):
    player = graphene.Field(PlayerType, id=graphene.ID(required=True))
    # all_players = graphene.List(PlayerType)
    all_players = graphene.List(PlayerType, school_name=graphene.String())
    
    
    def resolve_player(self, info, id):
        return Player.objects.get(id=id)

    # def resolve_all_players(self, info):
    #     return Player.objects.all()
    def resolve_all_players(self, info, school_name=None):
        qs = Player.objects.select_related("school").all()
        if school_name:
            qs = qs.filter(school__name__iexact=school_name)
        return qs
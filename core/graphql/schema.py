
import graphene
from core.graphql.queries.player import PlayerQuery

class PlayerGraphQLQuery(PlayerQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=PlayerGraphQLQuery)
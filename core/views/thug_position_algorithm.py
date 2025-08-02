from rest_framework import viewsets
from rest_framework.response import Response
from core.models.active_nfl_players import ActiveNFLPlayers
from core.serializers.active_nfl_player_serializer import ActiveNFLPlayerSerializer


class ThugPositionsBySchoolViewset(viewsets.ModelViewSet):
    """
    Thug Position Algorithm
        1. Active NFL Players by school
        2. # of players by Position
            Example: RB Example: 5 active RB’s
        3. The Depth Chart rank by Position (e.g. 1st string, 2nd, 3rd, etc...)
            RB Example: 4 are starters & 1 is a 2nd stringer
        4. The Draft Choice by Position (e.g. 1st round through undrafted)
            RB Example: 3 1st rounders, 1 in 2nd & 1 in 3rd. Average pick # of 40
        5. The (Avg Years of Experience) by Position
            RB Example: Derrick Henry has 10 YOE, Jacobs has 6, Gibbs has 2, so average would be 6 YOE for RB
    """
    def list(self, request, *args, **kwargs):
        active_players = ActiveNFLPlayers.objects.all()
        serialized_active_players = ActiveNFLPlayerSerializer(active_players, many=True)

        return Response(serialized_active_players.data)
    
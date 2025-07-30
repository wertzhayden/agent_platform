from rest_framework import viewsets
from rest_framework.response import Response

from core.models.player import Player
from core.filters.player import PlayerFilter  # adjust path if needed
from core.serializers.player_serializer import PlayerSerializer
    
# views.py

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend


class RetrievePlayersViewset(viewsets.ModelViewSet):
    """
    List and filter Player data (with flexibility for future custom logic).
    Supports filtering by related Recruit fields (e.g. stars, position, recruiting year).
    """
    def list(self, request, *args, **kwargs):
        """"""
        # players = Player.objects.select_related("school").prefetch_related("recruits").all()
        # serializer = PlayerSerializer(players, many=True)
        # return Response(serializer.data)

        # Helper to parse multi-value query params
        def parse_list_param(key):
            value = request.query_params.get(key)
            return [v.strip() for v in value.split(",")] if value else None
        players = Player.objects.select_related("school").prefetch_related(
            "recruits__recruiting_class",
            "qbcareerstats_career_stats",
            "rbcareerstats_career_stats",
            "receivercareerstats_career_stats",
            "defensecareerstats_career_stats",
        )

        # Apply filters
        conference_list = parse_list_param("school__conference")
        class_year_list = parse_list_param("class_year")
        position_list = parse_list_param("position")

        if conference_list:
            players = players.filter(school__conference__in=conference_list)
        if class_year_list:
            players = players.filter(class_year__in=class_year_list)
        if position_list:
            players = players.filter(position__in=position_list)

        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        players_by_school = Player.objects.filter(school__external_name__icontains="Alabama")
        serializer = PlayerSerializer(players_by_school, many=True)
        player_data = []

        for player in serializer.data:
            return Response(player)
        return Response("Hey Hayden")
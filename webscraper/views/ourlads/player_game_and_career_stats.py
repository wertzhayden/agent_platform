from rest_framework import viewsets
from rest_framework.response import Response

from webscraper.services.player_data.player_game_and_career_stats import retrieve_game_and_career_stats_of_all_players

class IngestPlayersGameAndCareerStats(viewsets.ViewSet):
    """
    Web Scrape Team and Player Stats from the Ourlads website. 
    """

    def create(self, request):
        incoming_school = request.data.get("school")
        if incoming_school:
            return Response(retrieve_game_and_career_stats_of_all_players(incoming_school=incoming_school))
        return Response(retrieve_game_and_career_stats_of_all_players())
    
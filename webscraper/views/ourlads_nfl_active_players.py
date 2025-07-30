from rest_framework import viewsets
from rest_framework.response import Response
from django.db import transaction

from core.models.active_nfl_players import ActiveNFLPlayers
from core.models.school import School
from core.serializers.active_nfl_player_serializer import ActiveNFLPlayerSerializer
from core.utils.pull_ourlads_depth_charts_helpers import split_name_into_first_and_last

from webscraper.constants.ourlads_constants import TEAM_IDS
from webscraper.services.player_data.retrieve_active_nfl_players_by_school import (
    retrieve_active_nfl_players_by_college,
)

class IngestActiveNFLPlayersBySchool(viewsets.ViewSet):
    """
    Web Scrape Team and Player Stats from the Ourlads website. 
    """
    def create(self, request):
        results = []

        if request.data.get("school") and request.data.get("school_id"):
            schools_to_process = {
                request.data["school"]: request.data["school_id"]
            }
        else:
            schools_to_process = TEAM_IDS

        for school, school_id in schools_to_process.items():
            school_obj = School.objects.filter(external_name=school).first()

            if school_obj is not None:
                deleted, _ = ActiveNFLPlayers.objects.filter(school=school_obj).delete()
                print(f"Deleted {deleted} active players for {school}")

            players = retrieve_active_nfl_players_by_college(school=school, school_id=school_id)

            for player_data in players:
                ourlads_link = player_data.get("ourlads_link")
                if not ourlads_link:
                    print(f"Missing URL for {player_data.get('name')}")
                    continue

                try:
                    with transaction.atomic():
                        active_player, created = ActiveNFLPlayers.objects.update_or_create(
                            ourlads_link=ourlads_link,
                            defaults={**player_data, "school": school_obj}
                        )
                        results.append(ActiveNFLPlayerSerializer(active_player).data)
                except Exception as e:
                    print(f"Failed to save player {player_data.get('name')}: {e}")
                    continue

        return Response(results)
        # for school, school_id in schools_to_process.items():
        #     school_obj = School.objects.filter(external_name=school).first()
        #     if school_obj:
        #       ActiveNFLPlayers.objects.filter(school=school_obj).delete()
        #     players = retrieve_active_nfl_players_by_college(school=school, school_id=school_id)
        #     for player_data in players:
        #         try:
        #             with transaction.atomic():
        #                 active_player, created = ActiveNFLPlayers.objects.update_or_create(
        #                     ourlads_link=player_data["ourlads_link"],
        #                     defaults={**player_data, "school": school_obj}
        #                 )
        #                 results.append(ActiveNFLPlayerSerializer(active_player).data)
        #         except Exception as e:
        #             print(f"Failed to save player {player_data.get('name')}: {e}")
        #             continue
        # return Response(results)

    

"""
Create a Viewset to scrape the Active NFL Players by School

- Build an Algorithm to determine the THUG Positions by School
  - Example: Determine the THUG Positions List for all Schools
    - WR Example: OSU is #1, Bama is #2, LSU is #3, etc. 
      - Build this Algorithm by: 
        1. # of active NFL players by position
        2. # of players drafted by position
        3. Draft Selection of each Positon
        4. NFL Depth Chart Position on their NFL Team

1. https://www.ourlads.com/ncaa-football-depth-charts/active-nfl-players-by-college/lsu/90981
2. https://www.ourlads.com/ncaa-football-depth-charts/active-nfl-players-by-college/alabama/89923
"""

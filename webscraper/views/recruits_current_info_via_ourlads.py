from rest_framework import viewsets
from rest_framework.response import Response

from webscraper.models.recruit import Recruit
from webscraper.services.player_hs_rankings.retrieve_latest_school_by_player import retrieve_latest_school_by_player


class IngestRecruitsCurrentData(viewsets.ViewSet):
    """
    Web Scrape Team and Player Stats from the Ourlads website. 
    """

    def create(self, request):
        return Response(retrieve_recruits_current_info_via_ourlads())

def retrieve_recruits_current_info_via_ourlads() -> list:
    """Retrieve the current information of recruits via Ourlads."""
    recruits = Recruit.objects.all()
    recruits_list = []
    for recruit in recruits:
        player_profile_url = recruit.school_link
        current_school_data = retrieve_latest_school_by_player(url=player_profile_url) or {}
        current_position = current_school_data.get("position")
        current_height = current_school_data.get("height")
        current_weight = current_school_data.get("weight")
        experience_level_at_current_school = current_school_data.get("exp")
        current_school = current_school_data.get("current_school")
        recruit.current_position = current_position
        recruit.current_height = current_height
        recruit.current_weight = current_weight
        recruit.experience_level_at_current_school = experience_level_at_current_school
        recruit.current_school = current_school
        recruit.save()
        recruits_list.append({
            "first_name": recruit.first_name,
            "last_name": recruit.last_name,
            "position": recruit.current_position,
            "height": recruit.current_height,
            "weight": recruit.current_weight,
            "experience_level_at_current_school": recruit.experience_level_at_current_school,
            "current_school": recruit.current_school
        })
    return Response(recruits_list)

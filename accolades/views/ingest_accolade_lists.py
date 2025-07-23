from rest_framework import viewsets
from rest_framework.response import Response

from accolades.models.accolade import Accolade
from accolades.serializer.accolade import AccoladeSerializer

from accolades.utils.ingest_accolades_lists import (
    accolades_configs,
    split_name_into_first_and_last, 
    ALL_ACCOLADES
)

from core.models.player import Player


class IngestAccoladesViewset(viewsets.ViewSet):
    """
    Web Scrape Team and Player Stats from the Ourlads website. 
    """

    def create(self, request):
        # accolades_list, awards = accolades_configs("freshman", "twenty_four_seven_sports")
        # accolades_list, awards = accolades_configs("all_american", "cfn")
        # accolades_list, awards = accolades_configs("all_conference", "aac")
    
        accolades = []
        for category, sources in ALL_ACCOLADES.items():
            for source in sources:
                accolades_list, awards = accolades_configs(name_of_award=category, accolade_list=source)
                # @TODO: Create a For Loop for each Accolade Config
                if not accolades_list:
                    return Response({"message": "No data found"}, status=404)
                # Move Config into Constants File
                for player in awards:
                    name = player.get("name")
                    first_name, last_name = split_name_into_first_and_last(name)
                    player_obj = Player.objects.filter(
                        first_name__iexact=first_name,
                        last_name__iexact=last_name,
                    ).first()

                    accolade, _ = Accolade.objects.get_or_create(
                        player=player_obj,
                        year=accolades_list.get("year"),
                        first_name=first_name,
                        last_name=last_name,
                        name_of_award=accolades_list.get("name_of_award"),
                        team=player.get("team", 1),
                        source=accolades_list.get("source"),
                        conference=accolades_list.get("conference"),
                        award=player.get("award"),
                    )
                    serializer = AccoladeSerializer(accolade)
                    accolades.append(serializer.data)
        return Response(accolades, status=200)

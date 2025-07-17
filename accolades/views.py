from rest_framework import viewsets
from rest_framework.response import Response
from accolades.accolade_data_lists.all_freshman_lists.twenty_twenty_four.two_four_seven_sports import TWO_FOUR_SEVEN_SPORTS
from accolades.accolade_data_lists.all_freshman_lists.twenty_twenty_four.freshman_all_sec import FRESHMEN_ALL_SEC
from accolades.accolade_data_lists.all_freshman_lists.twenty_twenty_four.on3 import ON_THREE_FRESHMEN
from accolades.accolade_data_lists.all_freshman_lists.twenty_twenty_four.pff import PFF_FRESHMEN
from accolades.accolade_data_lists.all_freshman_lists.twenty_twenty_four.pwaa import PWAA_FRESHMEN
from accolades.accolade_data_lists.all_freshman_lists.twenty_twenty_four.cfn import CFN_FRESHMEN
from accolades.accolade_data_lists.all_american_lists.twenty_twenty_four.cfn import CFN_ALL_AMERICAN

from accolades.accolade_data_lists.cfn_all_conference_lists.twenty_twenty_four.all_aac import ALL_AAC
from accolades.accolade_data_lists.cfn_all_conference_lists.twenty_twenty_four.all_acc import ALL_ACC
from accolades.accolade_data_lists.cfn_all_conference_lists.twenty_twenty_four.all_big_ten import ALL_BIG_TEN
from accolades.accolade_data_lists.cfn_all_conference_lists.twenty_twenty_four.all_big_twelve import ALL_BIG_TWELVE
from accolades.accolade_data_lists.cfn_all_conference_lists.twenty_twenty_four.all_c_usa import ALL_C_USA
from accolades.accolade_data_lists.cfn_all_conference_lists.twenty_twenty_four.all_mac import ALL_MAC
from accolades.accolade_data_lists.cfn_all_conference_lists.twenty_twenty_four.all_mountain_west import ALL_MOUNTAIN_WEST
from accolades.accolade_data_lists.cfn_all_conference_lists.twenty_twenty_four.all_sec import ALL_SEC
from accolades.accolade_data_lists.cfn_all_conference_lists.twenty_twenty_four.all_sun_belt import ALL_SUN_BELT

from accolades.models.accolade import Accolade
from accolades.serializer.accolade import AccoladeSerializer

from core.models.player import Player


def split_name_into_first_and_last(full_name: str) -> tuple:
    if "," in full_name:
        last_name, first_name = full_name.split(",", 1)
        return first_name.strip(), last_name.strip()
    if " " in full_name:
        first_name, last_name = full_name.split(" ", 1)
        return first_name.strip(), last_name.strip()
    return full_name.strip(), ""  # Fallback if no comma

ALL_ACCOLADES = {
    "freshman": {
        "twenty_four_seven_sports": TWO_FOUR_SEVEN_SPORTS,
        "sec": FRESHMEN_ALL_SEC,
        "on3": ON_THREE_FRESHMEN,
        "pff": PFF_FRESHMEN,
        "pwaa": PWAA_FRESHMEN,
        "cfn": CFN_FRESHMEN,
    },
    "all_american": {
        "cfn": CFN_ALL_AMERICAN,
    },
    "all_conference": {
        "aac": ALL_AAC,
        "acc": ALL_ACC,
        "big_ten": ALL_BIG_TEN,
        "big_twelve": ALL_BIG_TWELVE,
        "c_usa": ALL_C_USA,
        "mac": ALL_MAC,
        "mountain_west": ALL_MOUNTAIN_WEST, 
        "sec": ALL_SEC,
        "sun_belt": ALL_SUN_BELT
    },
}

def accolades_configs(name_of_award: str, accolade_list: dict) -> dict:
    """Return the configuration for the accolades"""
    accolades_list = ALL_ACCOLADES.get(name_of_award, {}).get(accolade_list)
    awards = accolades_list.get(accolade_list)
    return accolades_list, awards



class IngestAccoladesViewset(viewsets.ViewSet):
    """
    Web Scrape Team and Player Stats from the Ourlads website. 
    """

    def list(self, request):
        # accolades_list, awards = accolades_configs("freshman", "twenty_four_seven_sports")
        # accolades_list, awards = accolades_configs("freshman", "sec")
        # accolades_list, awards = accolades_configs("freshman", "on3")
        # accolades_list, awards = accolades_configs("freshman", "pff")
        # accolades_list, awards = accolades_configs("freshman", "pwaa")
        # accolades_list, awards = accolades_configs("freshman", "cfn")
        # accolades_list, awards = accolades_configs("all_american", "cfn")
        # accolades_list, awards = accolades_configs("all_conference", "aac")
        # accolades_list, awards = accolades_configs("all_conference", "acc")
        # accolades_list, awards = accolades_configs("all_conference", "big_ten")
        # accolades_list, awards = accolades_configs("all_conference", "big_twelve")
        # accolades_list, awards = accolades_configs("all_conference", "c_usa")
        # accolades_list, awards = accolades_configs("all_conference", "mac")
        # accolades_list, awards = accolades_configs("all_conference", "mountain_west")
        # accolades_list, awards = accolades_configs("all_conference", "sec")
        accolades_list, awards = accolades_configs("all_conference", "sun_belt")

        # @TODO: Create a For Loop for each Accolade Config
        if not accolades_list:
            return Response({"message": "No data found"}, status=404)
        accolades = []
        # Move Config into Constants File
        for player in awards:
            name = player.get("name")
            first_name, last_name = split_name_into_first_and_last(name)
            player_obj = Player.objects.filter(
                first_name__iexact=first_name,
                last_name__iexact=last_name,
                school__name__iexact=player.get("school")
            ).first()
            # return Response(player)

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

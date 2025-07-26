from rest_framework import viewsets
from rest_framework.response import Response

from core.models.player import Player
from core.models.school import School

from webscraper.constants.ourlads_constants import TEAM_IDS
from webscraper.services.player_data.retrieve_team_depth_chart import retrieve_schools_players_by_depth_chart
from webscraper.serializers.player_serializer import PlayerSerializer
from core.utils.pull_ourlads_depth_charts_helpers import (
    determine_ourlads_player_name_and_class,
)

def format_school_name(name: str) -> str:
    exceptions = {
        "smu": "SMU", 
        "brigham-young": "BYU",
        "central-florida": "UCF",
        "central-michigan": "CMU",
        "connecticut": "UConn",
        "east-carolina": "ECU",
        "eastern-michigan": "EMU",
        "florida-atlantic": "FAU",
        "florida-international": "FIU",
        "james-madison": "JMU",
        "louisiana": "UL Lafayette",
        "louisiana-tech": "La Tech",
        "louisiana-monroe": "UL Monroe",
        "lsu": "LSU",
        "umass": "UMass",
        "miami-university": "Miami of Ohio",
        "north-carolina": "UNC",
        "pittsburgh": "Pitt",
        "south-florida": "USF",
        "tcu": "TCU",
        "texas-am": "Texas A&M",
        "uab": "UAB",
        "ucla": "UCLA",
        "unlv": "UNLV",
        "usc": "USC",
        "utep": "UTEP",
        "utsa": "UTSA",
    }
    return exceptions.get(name, name.replace("-", " ").title())

class IngestOurladsDepthCharts(viewsets.ViewSet):
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
            players_by_position = retrieve_schools_players_by_depth_chart(
                school=school,
                school_id=school_id
            )

            school_data = {
                "name": format_school_name(school),
                "external_name": school,
                "school_id": school_id,
            }

            school_obj, _ = School.objects.update_or_create(
                school_id=school_id,
                defaults=school_data
            )

            for pos in players_by_position:
                for idx, p in enumerate(pos.get("players", [])):
                    ourlads_name = p.get("name")
                    if not ourlads_name:
                        continue
                    name_and_class = determine_ourlads_player_name_and_class(ourlads_name=ourlads_name)

                    player_data = {
                        "first_name": name_and_class.get("first_name"),
                        "last_name": name_and_class.get("last_name"),
                        "class_year": name_and_class.get("class"),
                        "jersey_number": p.get("number") or None,
                        "position": p.get("position"),
                        "school": school_obj.id,
                        "ourlads_link": p.get("url"),
                        "depth_chart_position": idx + 1,
                        "estimated_eligibility_left": name_and_class.get("years_left_of_eligibility"),
                        "side_of_ball": p.get("side_of_the_ball"),
                    }
                    if not player_data.get("first_name") or not player_data.get("last_name"):
                        # continue
                        return Response([p, name_and_class])
                    player_serializer = PlayerSerializer(data=player_data)
                    player_serializer.is_valid(raise_exception=True)

                    player, created = Player.objects.update_or_create(
                        ourlads_link=p["url"],
                        defaults={**player_data, "school": school_obj}
                    )

                    results.append({
                        "player": f"{player.first_name} {player.last_name}",
                        "school": school_obj.name,
                        "jersey_number": player.jersey_number,
                        "created": created,
                    })

        return Response({"status": "ok", "players_processed": results})


    
"""
Remaining Lists to Scrape:

1. PFF Freshman All-American List - COMPLETE
2. PWAA Freshman All-American List - COMPLETE
3. 247sports Freshman All-American List - COMPLETE
4. College Football News (CFN) Freshman All-American List - COMPLETE
5. on3 Freshman All-American List - COMPLETE
6. Freshman ALL-SEC List - COMPLETE 
7. CFN All-AAC List - COMPLETE
8. CFN All-ACC List - COMPLETE
7. CFN All-Big-10 List - COMPLETE
9. CFN All-Big-12 List - COMPLETE
10. CFN All-CUSA List - COMPLETE
11. CFN All-MAC List - COMPLETE
12. CFN All-MWC List - COMPLETE
13. CFN All-Pac-12 List - COMPLETE
14. CFN All-SEC List - COMPLETE
15. CFN All-Sun-Belt List - COMPLETE
16. Shawn Alexander Freshman Semi-Finalists List - 
17. ...
"""
import re
from rest_framework import viewsets
from rest_framework.response import Response
from webscraper.services.player_data.retrieve_team_depth_chart import retrieve_schools_players_by_depth_chart
from webscraper.services.player_data.retrieve_player_stats import retrieve_player_stats
from webscraper.services.player_hs_rankings.retrieve_hs_rankings import retrieve_player_hs_rankings
from webscraper.services.player_hs_rankings.retrieve_latest_school_by_player import retrieve_latest_school_by_player
from webscraper.constants.ourlads_constants import TEAM_IDS
from core.models.player import Player
from core.models.school import School
from webscraper.serializers.player_serializer import PlayerSerializer
from webscraper.serializers.school_serializer import SchoolSerializer

CLASSES = ["RS", "FR", "SO", "JR", "SR", "GR"]
YEARS_LEFT_OF_ELIGIBILITY = {
    "FR": 4,
    "SO": 3,
    "JR": 2,
    "SR": 1,
    "GR": 1
}

def determine_years_left_of_eligibility(class_year: str) -> int:
    """Determines the years left of eligibility based on the class year."""
    eligibility_year = YEARS_LEFT_OF_ELIGIBILITY.keys()
    for year in eligibility_year:
        if year in class_year:
            return YEARS_LEFT_OF_ELIGIBILITY[year]
    return eligibility_year

def find_first_class_index(tokens):
    for i, token in enumerate(tokens):
        if any(cls in token for cls in CLASSES):
            return i
    return -1  # Not found

def split_name_into_first_and_last(full_name: str) -> tuple:
    if "," in full_name:
        last_name, first_name = full_name.split(",", 1)
        return first_name.strip(), last_name.strip()
    return full_name.strip(), ""  # Fallback if no comma


def determine_ourlads_player_name_and_class(ourlads_name: str) -> dict: 
        """Determines the player's name and class from the Ourlads website."""
        # Split the Name & Class 
        name = ourlads_name.split(" ")
        first_class_index = find_first_class_index(name)
        # Both split out here
        full_name = name[:first_class_index] if first_class_index != -1 else []
        class_suffix = name[first_class_index:] if first_class_index != -1 else name
        # Separate the First & Last Name
        full_name = " ".join(full_name).strip()
        first_name, last_name = split_name_into_first_and_last(full_name=full_name)
        # Separate the Class Suffix
        class_suffix = " ".join(class_suffix).strip() if class_suffix else ""
        # Determine the Years Left of Eligibility
        years_left_of_eligibility = determine_years_left_of_eligibility(class_suffix)

        return {
            "first_name": first_name,
            "last_name": last_name,
            "class": class_suffix,
            "years_left_of_eligibility": years_left_of_eligibility
        }

OURLADS_POSSIBLE_POSITIONS = ["QB", "RB", "WR", "TE", "DL", "LB", "DB", "K", "P"]
def determine_ourlads_position(position: str, side_of_ball: str) -> str:
    """Determine whether to include the Career / Game Stats Headers for the Position"""
    if not position or not side_of_ball:
        return None
    position = position.lower() if type(position) is str else position
    side_of_ball = side_of_ball.lower() if type(side_of_ball) is str else side_of_ball
    if side_of_ball == "offense":
        if "rb" in position or "fb" in position:
            return "rb"
        if "wr" or "te" in position:
            return "wr"
    return None

def convert_ourlads_height_and_weight_from_players_page(ht_wt_string: str) -> tuple:
    if not ht_wt_string:
        return None, None
    split_values = [part.strip() for part in ht_wt_string.split("|")]
    for value in split_values:
        if "ht" in value.lower():
            height = int(re.search(r"\d+", value).group())
        elif "wt" in value.lower():
            weight = int(re.search(r"\d+", value).group())
    return height, weight

def convert_ourlads_hometown_and_high_school(hometown_data: str) -> tuple:
    if not hometown_data:
        return None, None, None
    split_values = [part.strip() for part in hometown_data.split("|")]
    hometown = split_values[0].split(":")[1].strip().split(",")
    city = hometown[0].strip() if len(hometown) > 0 else ""
    state = hometown[1].strip() if len(hometown) > 1 else ""
    high_school = split_values[1].split(":")[1].strip()
    return city, state, high_school


class IngestOurladsDepthCharts(viewsets.ViewSet):
    """
    Web Scrape Team and Player Stats from the Ourlads website. 
    """

    def list(self, request):    
        players = Player.objects.all()
        player_serializer = PlayerSerializer(players, many=True)
        for player in player_serializer.data:
            position = determine_ourlads_position(
                position=player.get("position"),
                side_of_ball=player.get("side_of_ball")
            )
            player_stats = retrieve_player_stats(position=position, player_link=player.get("ourlads_link"))
            # return Response(player_stats)
            height, weight = convert_ourlads_height_and_weight_from_players_page(ht_wt_string=player_stats.get("bio", {}).get("physical_stats"))
            city, state, high_school = convert_ourlads_hometown_and_high_school(hometown_data=player_stats.get("bio", {}).get("hometown_highschool"))
            schools_attended = player_stats.get("bio", {}).get("transfer_schools")
            # school_link = player_stats.get("player_links", {})[0].get("href")
            # @TODO: Save the CAREER & GAME stats 
            career_stats = player_stats.get("career_stats", [])
            game_stats = player_stats.get("game_stats", [])
            if career_stats:
                for career_stat in career_stats:
                    return Response(career_stat)

            
        return Response(player_serializer.data)
        schools_to_process = [{"school": name, "school_id": sid} for name, sid in TEAM_IDS.items()]
        # return Response(schools_to_process)
        return Response(retrieve_player_stats(position=request.data.get("position"), player_link=request.data.get("player_link")))
        # return Response(retrieve_player_hs_rankings(school=request.data.get("school"), year=request.data.get("year")))
        # return Response(retrieve_latest_school_by_player(url=request.data.get("url")))

    def create(self, request):
        results = []
        if request.data.get("school") and request.data.get("school_id"):
            schools_to_process = [{
                "school": request.data.get("school"),
                "school_id": request.data.get("school_id")
            }]
        else:
            # Fallback to all Team IDs
            schools_to_process = [{"school": name, "school_id": sid} for name, sid in TEAM_IDS.items()]
        
        for school_entry in schools_to_process:
            school_name = school_entry["school"]
            school_id = school_entry["school_id"]
            players_by_position = retrieve_schools_players_by_depth_chart(
                school=school_name,
                school_id=school_id
            )
            school_data = {
                "name": school_name,
                "external_name": school_name,
                "school_id": school_id,
            }

            school, _ = School.objects.get_or_create(
                school_id=school_data["school_id"],
                defaults=school_data
            )
            for pos in players_by_position:
                players = pos.get("players", [])
                for idx, p in enumerate(players):
                    ourlads_name = p.get("name")
                    name_and_class = determine_ourlads_player_name_and_class(ourlads_name=ourlads_name)

                    player_data = {
                        "first_name": name_and_class.get("first_name"),
                        "last_name": name_and_class.get("last_name"),
                        "class_year": name_and_class.get("class"),
                        "jersey_number": p.get("number") if p.get("number") and type(p.get("number")) is int else None,
                        "position": p.get("position"),
                        "school": school.id,
                        "ourlads_link": p.get("url"),
                        "depth_chart_position": idx + 1,
                        "estimated_eligibility_left": name_and_class.get("years_left_of_eligibility"),
                        "side_of_ball": p.get("side_of_the_ball"),
                    }

                    player_serializer = PlayerSerializer(data=player_data)
                    player_serializer.is_valid(raise_exception=True)

                    player, created = Player.objects.get_or_create(
                        player_ourlads_link=p["url"],
                        defaults={**player_data, "school": school}
                    )

                    results.append({
                        "player": f"{player.first_name} {player.last_name}",
                        "school": school.name,
                        "created": created,
                    })
        return Response({"status": "ok", "players_processed": len(results)})
    
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
9. CFN All-Big-12 List - ...
10. CFN All-CUSA List -
11. CFN All-MAC List -
12. CFN All-MWC List -
13. CFN All-Pac-12 List -
14. CFN All-SEC List -
15. CFN All-Sun-Belt List -
16. Shawn Alexander Freshman Semi-Finalists List - 
17. ...
"""
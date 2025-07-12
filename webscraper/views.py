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
from webscraper.serializers.career_stats.qb import QBCareerStatsSerializer
from webscraper.serializers.career_stats.rb import RBCareerStatsSerializer
from webscraper.serializers.career_stats.wr import ReceiverCareerStatsSerializer
from webscraper.serializers.career_stats.defense import DefenseCareerStatsSerializer

from webscraper.serializers.game_stats.qb import QBGameStatsSerializer
from webscraper.serializers.game_stats.rb import RBGameStatsSerializer
from webscraper.serializers.game_stats.wr import ReceiverGameStatsSerializer
from webscraper.serializers.game_stats.defense import DefenseGameStatsSerializer

from webscraper.models.recruiting_class import RecruitingClass
from webscraper.models.recruit import Recruit

CAREER_STATS_SERIALIZER_MAP = {
    "qb": QBCareerStatsSerializer,
    "rb": RBCareerStatsSerializer,
    "wr": ReceiverCareerStatsSerializer,
    "defense": DefenseCareerStatsSerializer,
}

GAME_STATS_SERIALIZER_MAP = {
    "qb": QBGameStatsSerializer,
    "rb": RBGameStatsSerializer,
    "wr": ReceiverGameStatsSerializer,
    "defense": DefenseGameStatsSerializer,
}

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
    position = position.lower() if position else position
    side_of_ball = side_of_ball.lower() if side_of_ball else side_of_ball
    if side_of_ball == "offense":
        if "rb" in position or "fb" in position:
            return "rb"
        if "wr" in position or "te" in position:
            return "wr"
        if "qb" in position:
            return "qb"
    return "defense"

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

def split_high_school_and_hometown(school_location: str) -> tuple:
    if "(" in school_location and ")" in school_location:
        high_school, hometown_part = school_location.split("(", 1)
        high_school = high_school.strip()
        hometown_part = hometown_part.rstrip(")").strip()

        if "," in hometown_part:
            city, state = map(str.strip, hometown_part.split(",", 1))
        else:
            city, state = hometown_part, None
    else:
        high_school = school_location.strip()
        city, state = None, None

    return high_school, city, state


class IngestOurladsDepthCharts(viewsets.ViewSet):
    """
    Web Scrape Team and Player Stats from the Ourlads website. 
    """

    def list(self, request):
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


        # return Response(get_hs_rankings_by_school_and_year(school=request.data.get("school"), year=request.data.get("year")))
        
        # return Response(retrieve_latest_school_by_player(url=request.data.get("url")))

    


    def retrieve_game_and_career_stats_of_all_players(self, request):    
        players = Player.objects.all()
        all_results = []

        for player in players:  # ✅ Loop over model instances

            # Skip special teams players
            if (player.side_of_ball or "").strip().lower() == "special teams":
                continue

            position = determine_ourlads_position(
                position=player.position,
                side_of_ball=player.side_of_ball
            )

            player_stats = retrieve_player_stats(
                player_link=player.ourlads_link,
                position=position
            )

            # Parse and assign player attributes
            height, weight = convert_ourlads_height_and_weight_from_players_page(
                ht_wt_string=player_stats.get("bio", {}).get("physical_stats")
            )
            city, state, high_school = convert_ourlads_hometown_and_high_school(
                hometown_data=player_stats.get("bio", {}).get("hometown_highschool")
            )
            schools_attended = player_stats.get("bio", {}).get("transfer_schools")

            # Ensure it's a list
            if isinstance(schools_attended, str):
                schools_attended = [schools_attended]
            elif schools_attended is None:
                schools_attended = []

            # Save to Player model
            player.height = height
            player.weight = weight
            player.hometown_city = city
            player.hometown_state = state
            player.high_school = high_school
            player.schools_attended = schools_attended
            player.save()

            # --- Save Career Stats ---
            career_stats = player_stats.get("career_stats", [])
            if not career_stats:
                continue

            for career_stat in career_stats:
                serializer_class = CAREER_STATS_SERIALIZER_MAP.get(position)
                if not serializer_class:
                    continue 

                career_stat["player"] = player.id
                try:
                    serializer = serializer_class(data=career_stat)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    all_results.append(serializer.data)
                except Exception as e:
                    return Response(
                        {
                            "error": "Career stat validation failed",
                            "error_msg": getattr(e, 'detail', str(e)),
                            "ourlads_position": position,
                            "player_id": player.id,
                            "career_stat": career_stat,
                        },
                        status=400
                    )

            # --- Save Game Stats ---
            game_stats = player_stats.get("game_stats", [])
            for game in game_stats:
                serializer_class = GAME_STATS_SERIALIZER_MAP.get(position)
                if not serializer_class:
                    continue

                game["player"] = player.id
                try:
                    serializer = serializer_class(data=game)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    all_results.append(serializer.data)
                except Exception as e:
                    return Response(
                        {
                            "error": "Game stat validation failed",
                            "error_msg": getattr(e, 'detail', str(e)),
                            "ourlads_position": position,
                            "player_id": player.id,
                            "game": game,
                        },
                        status=400
                    )

        return Response([len(all_results), all_results])
        # schools_to_process = [{"school": name, "school_id": sid} for name, sid in TEAM_IDS.items()]
        # return Response(schools_to_process)
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
                        "jersey_number": p.get("number") if p.get("number") else None,
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
                        ourlads_link=p["url"],
                        defaults={**player_data, "school": school}
                    )

                    results.append({
                        "player": f"{player.first_name} {player.last_name}",
                        "school": school.name,
                        # @TODO: MAKE SURE JERSEY NUMBER IS SAVED !!!s
                        "jersey_number": player.jersey_number,
                        "created": created,
                    })
        return Response({"status": "ok", "players_processed": results})
    

def get_hs_rankings_by_school_and_year(school: str, year: int) -> dict:
        """
        Get the high school rankings for a specific school and year.
        """
        school_name = school
        year = year
        school = School.objects.filter(name=school_name).first()

        hs_rankings = retrieve_player_hs_rankings(school=school_name, year=year)
        recruiting_class_rank = hs_rankings.get("ranks", {})
        # Safely extract ranks
        overall_rank = recruiting_class_rank.get("overall_rank", {}).get("value")
        transfer_rank = recruiting_class_rank.get("transfer_rank", {}).get("value")
        composite_rank = recruiting_class_rank.get("composite_rank", {}).get("value")

        recruiting_class, _ = RecruitingClass.objects.get_or_create(
            school=school,
            year=year,
            defaults={
                "overall_rank": overall_rank,
                "transfer_rank": transfer_rank,
                "composite_rank": composite_rank,
            },
        )

        results = []

        def parse_name(full_name):
            name_parts = full_name.split(" ", 1)
            return name_parts[0], name_parts[1] if len(name_parts) > 1 else ""

        def parse_ht_wt(ht_wt):
            parts = ht_wt.split("/")
            height = parts[0].strip() if len(parts) > 0 else None
            weight = parts[1].strip() if len(parts) > 1 else None
            return height, weight

        # --- Handle Recruits ---
        for player in hs_rankings.get("players", []):
            if not player.get("name"):
                continue
            first_name, last_name = parse_name(player["name"])
            height, weight = parse_ht_wt(player.get("ht_wt", ""))
            profile_url = f"https:{player.get("profile_url")}"
            position = player.get("position", "").lower()
            stars = player.get("stars")
            hs_rating_score = player.get("rating_score")
            national_rank = player.get("national_rank") if isinstance(player.get("national_rank"), int) else None
            position_rank = player.get("position_rank") if isinstance(player.get("position_rank"), int) else None
            state_rank = player.get("state_rank") if isinstance(player.get("state_rank"), int) else None
            status = player.get("status")
            hs, city, state = split_high_school_and_hometown(player.get("school_location"))
            # current_school_data = retrieve_latest_school_by_player(url=profile_url) or {}
            # current_position = current_school_data.get("position")
            # current_height = current_school_data.get("height")
            # current_weight = current_school_data.get("weight")
            # experience_level_at_current_school = current_school_data.get("exp")
            # current_school = current_school_data.get("school")
            recruit, _ = Recruit.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                position=position,
                high_school=hs,
                hometown_city=city,
                hometown_state=state,
                recruiting_class=recruiting_class,
                defaults={
                    "height": height,
                    "weight": weight,
                    "stars": stars,
                    "hs_rating_score": round(float(hs_rating_score), 2),
                    "national_rank": national_rank,
                    "position_rank": position_rank,
                    "state_rank": state_rank,
                    "status": status,
                    "school_link": profile_url,
                    # "current_position": current_position,
                    # "current_height": current_height,   
                    # "current_weight": current_weight,
                    # "experience_level_at_current_school": experience_level_at_current_school,
                    # "current_school": current_school,
                }
            )
            results.append({
                "name": f"{first_name} {last_name}",
                "type": "hs",
                "id": recruit.id,
                "school_link": recruit.school_link,
            })

        # --- Handle Transfers ---
        for transfer in hs_rankings.get("transfers", []):
            if not transfer.get("name"):
                continue

            first_name, last_name = parse_name(transfer["name"])
            height, weight = parse_ht_wt(transfer.get("ht_wt", ""))
            profile_url = transfer.get("profile_url")
            position = transfer.get("position", "").lower()
            # current_school_data = retrieve_latest_school_by_player(url=profile_url) or {}
            # current_position = current_school_data.get("position")
            # current_height = current_school_data.get("height")
            # current_weight = current_school_data.get("weight")
            # experience_level_at_current_school = current_school_data.get("exp")
            # current_school = current_school_data.get("school")
            hs_stars = hs_rating_score = transfer_stars = transfer_rating_score = None
            for rating in transfer.get("ratings", []):
                level = rating.get("level", "").lower()
                if level == "transfer":
                    transfer_stars = rating.get("stars")
                    transfer_rating_score = rating.get("rating_score")
                elif level == "hs":
                    hs_stars = rating.get("stars")
                    hs_rating_score = rating.get("rating_score")
            recruit, _ = Recruit.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                position=position,
                high_school=None,
                hometown_city=None,
                hometown_state=None,
                recruiting_class=recruiting_class,
                defaults={
                    "height": height,
                    "weight": weight,
                    "stars": hs_stars,
                    "school_link": profile_url,
                #     "current_position": current_position,
                #     "current_height": current_height,   
                #     "current_weight": current_weight,
                #     "experience_level_at_current_school": experience_level_at_current_school,
                #     "current_school": current_school,
                }
            )
            if hs_stars is not None:
                recruit.stars = hs_stars
            if hs_rating_score is not None:
                recruit.rating_score = convert_string_to_float(hs_rating_score)
            if transfer_stars is not None:
                recruit.transfer_stars = transfer_stars
            if transfer_rating_score is not None:
                recruit.transfer_rating_score = convert_string_to_float(transfer_rating_score)
            recruit.save()

            results.append({
                "name": f"{first_name} {last_name}",
                "type": "transfer",
                "id": recruit.id,
                "school_link": recruit.school_link,
            })

        return {
            "recruiting_class": {
                "id": recruiting_class.id,
                "school": school_name,
                "year": year,
                "overall_rank": overall_rank,
                "transfer_rank": transfer_rank,
                "composite_rank": composite_rank
            },
            "recruits": results
        }

def convert_string_to_float(value: str) -> float:
    """
    Rounds a numeric string to two decimal places.

    Args:
        value (str): A string representing a numeric value.

    Returns:
        float: The numeric value rounded to two decimal places.
               Returns None if the input value is empty or None.
    """
    if not value:
        return None
    return round(float(value), 2)

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
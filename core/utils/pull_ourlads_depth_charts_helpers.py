import re

from webscraper.serializers.career_stats.qb import QBCareerStatsSerializer
from webscraper.serializers.career_stats.rb import RBCareerStatsSerializer
from webscraper.serializers.career_stats.wr import ReceiverCareerStatsSerializer
from webscraper.serializers.career_stats.defense import DefenseCareerStatsSerializer

from webscraper.serializers.game_stats.qb import QBGameStatsSerializer
from webscraper.serializers.game_stats.rb import RBGameStatsSerializer
from webscraper.serializers.game_stats.wr import ReceiverGameStatsSerializer
from webscraper.serializers.game_stats.defense import DefenseGameStatsSerializer

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
    return None

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


# def determine_ourlads_player_name_and_class(ourlads_name: str) -> dict: 
#         """Determines the player's name and class from the Ourlads website."""
#         # Split the Name & Class 
#         name = ourlads_name.split(" ")
#         first_class_index = find_first_class_index(name)
#         # Both split out here
#         full_name = name[:first_class_index] if first_class_index != -1 else []
#         class_suffix = name[first_class_index:] if first_class_index != -1 else name
#         # Separate the First & Last Name
#         full_name = " ".join(full_name).strip()
#         first_name, last_name = split_name_into_first_and_last(full_name=full_name)
#         # Separate the Class Suffix
#         class_suffix = " ".join(class_suffix).strip() if class_suffix else ""
#         # Determine the Years Left of Eligibility
#         years_left_of_eligibility = determine_years_left_of_eligibility(class_suffix)
#         return {
#             "first_name": first_name,
#             "last_name": last_name,
#             "class": class_suffix,
#             "years_left_of_eligibility": years_left_of_eligibility
#         }
def determine_ourlads_player_name_and_class(ourlads_name: str) -> dict:
    """Parses Ourlads name format into first name, last name, and class."""
    if "," not in ourlads_name:
        return {
            "first_name": "",
            "last_name": "",
            "class": "",
            "years_left_of_eligibility": 0
        }

    last_name_part, rest = ourlads_name.split(",", 1)
    last_name = last_name_part.strip()
    rest_tokens = rest.strip().split()

    first_name = rest_tokens[0] if len(rest_tokens) > 0 else ""
    class_suffix = rest_tokens[-1] if len(rest_tokens) > 1 else ""

    years_left = determine_years_left_of_eligibility(class_suffix)

    return {
        "first_name": first_name,
        "last_name": last_name,
        "class": class_suffix,
        "years_left_of_eligibility": years_left
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

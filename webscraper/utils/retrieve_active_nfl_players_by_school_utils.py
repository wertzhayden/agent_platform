from webscraper.constants.list_of_nfl_teams import NFL_TEAMS

def convert_nfl_team_abbreviation_to_full_name(abbreviated_team_name: str) -> str:
    """Converts an NFL team abbreviation to its full name"""
    return NFL_TEAMS.get(abbreviated_team_name)


def convert_to_ourlads_position_and_depth_chart_rank(chart_position: str) -> dict | None:
    """
    Convert chart string like:
    - "NT - 1st" ➜ {"ourlads_position": "NT", "depth_chart_position": 1, ...}
    - "H - 1st, PT - 1st" ➜ includes second position and rank
    """
    if not chart_position:
        return None

    parts = [part.strip() for part in chart_position.split(",")]
    primary_pos, primary_rank = None, None
    secondary_pos, secondary_rank = None, None

    def parse_rank(text):
        return int(text.replace("st", "").replace("nd", "").replace("rd", "").replace("th", ""))

    if len(parts) >= 1:
        sub = parts[0].split(" - ")
        if len(sub) == 2:
            primary_pos = sub[0].strip()
            primary_rank = parse_rank(sub[1].strip())

    if len(parts) == 2:
        sub = parts[1].split(" - ")
        if len(sub) == 2:
            secondary_pos = sub[0].strip()
            secondary_rank = parse_rank(sub[1].strip())

    return {
        "ourlads_position": primary_pos,
        "depth_chart_position": primary_rank,
        "ourlads_second_position": secondary_pos,
        "depth_chart_second_position": secondary_rank
    }


def convert_draft_status_to_year_round_and_overall_pick(draft_status: str) -> tuple | None:
    """Convert draft status to structured data:
    - "17 02 055" → (2017, 2, 55)
    - "24 CFA" → (2024, None, 'undrafted')
    """
    if not draft_status:
        return None, None, None

    parts = draft_status.strip().split()
    if len(parts) == 3:
        try:
            year = int(f"20{parts[0]}")
            round_ = int(parts[1])
            overall_pick = int(parts[2])
            return year, round_ , overall_pick
        except ValueError:
            return None, None, None
    elif len(parts) == 2 and parts[1].upper() == "CFA":
        try:
            year = int(f"20{parts[0]}")
            return year, None, "undrafted"
        except ValueError:
            return None, None, None
    else:
        return None, None, None

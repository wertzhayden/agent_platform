import requests
from bs4 import BeautifulSoup

from core.utils.pull_ourlads_depth_charts_helpers import split_name_into_first_and_last
from webscraper.utils.retrieve_active_nfl_players_by_school_utils import (
    convert_to_ourlads_position_and_depth_chart_rank,
    convert_draft_status_to_year_round_and_overall_pick,
    convert_nfl_team_abbreviation_to_full_name,
)

def retrieve_active_nfl_players_by_college(school: str, school_id: int) -> dict:
    """
    Scrapes active NFL players from the Ourlads page for a given school.
    
    Args:
        school (str): Name of the school used in the URL (e.g., 'kentucky')
        school_id (int): The Ourlads numeric ID for the school

    Returns:
        dict: List of active NFL players with metadata
    """
    if not school:
        return {"error": "School name is required."}
    if not school_id:
        return {"error": "School ID is required."}
    
    url = f"https://www.ourlads.com/ncaa-football-depth-charts/active-nfl-players-by-college/{school}/{school_id}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    players = []

    tbody = soup.find("tbody", id="ctl00_phContent_dcTBody")
    if not tbody:
        return {"error": "NFL players table not found."}

    # rows = tbody.find_all("tr", class_="row-dc-wht")
    rows = tbody.find_all("tr", class_=["row-dc-wht", "row-dc-grey"])
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue

        # Extract each column based on the visual structure
        try:
            team_img = cols[0].find("img")["alt"] if cols[0].find("img") else ""
            player_link_tag = cols[1].find("a")
            player_name = player_link_tag.get_text(strip=True) if player_link_tag else cols[1].text.strip()
            player_url = player_link_tag["href"] if player_link_tag else ""

            pos = cols[2].text.strip()
            chart_pos = cols[3].text.strip()
            status = cols[4].text.strip()
            draft_status = cols[5].text.strip()

            positions = convert_to_ourlads_position_and_depth_chart_rank(chart_position=chart_pos)
            year, round, overall_pick = convert_draft_status_to_year_round_and_overall_pick(draft_status=draft_status)
            first_name, last_name = split_name_into_first_and_last(full_name=player_name)
    
            players.append({
                "first_name": first_name,
                "last_name": last_name,
                "team": convert_nfl_team_abbreviation_to_full_name(abbreviated_team_name=team_img),
                "position": pos,
                "ourlads_position": positions.get("ourlads_position") if positions else None,
                "ourlads_second_position": positions.get("ourlads_second_position") if positions else None,
                "depth_chart_position": positions.get("depth_chart_position") if positions else None,
                "depth_chart_second_position": positions.get("depth_chart_second_position") if positions else None,
                "roster_status": status,
                "ourlads_link": f"https://www.ourlads.com{player_url}" if player_url.startswith("/") else player_url,
                "draft_year": year,
                "draft_round": round,
                "overall_draft_pick": overall_pick,
            })
        except Exception as e:
            print(f"Skipping row due to error: {e}")
            continue
    return players
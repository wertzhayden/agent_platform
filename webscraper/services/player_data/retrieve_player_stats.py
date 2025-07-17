import requests
from bs4 import BeautifulSoup
from webscraper.utils.webscraper_utils import determine_ourlads_headers_by_position


def retrieve_player_stats(player_link: str, position: str = None) -> dict:
    """
    Given a relative player_link like 'https://www.ourlads.com/ncaa-football-depth-charts/player/isaiah-horton/157217',
    fetches and parses player bio and stats including:
      - Player bio (name, position, school, height, weight, etc.)
      - Career stats
      - Game-by-game stats
      - Player links (like Bio)

    The `position` parameter will be used to determine the headers for career and game stats.
    """
    if not player_link:
        return {"error": "An Ourlads URL for the Player is required."}

    """
    These are the unique headers, based on position. Each Needs Career & Game Stats Headers
    QB's 
    RB's
    WR's / TE's
    Defense
    """
    response = requests.get(player_link)
    soup = BeautifulSoup(response.content, 'html.parser')
    player_bio_data = {}

    # Player photo
    photo_tag = soup.find("img", id="ctl00_phContent_iHS")
    # Actual Photo URL: https://www.ourlads.com/images/players/ncaa/HOR292292.png
    player_bio_data["photo_url"] = "https://www.ourlads.com" + photo_tag["src"] if photo_tag else None

    # Player name
    name_tag = soup.find("h1", id="ctl00_phContent_hTitle")
    player_bio_data["name"] = name_tag.get_text(strip=True) if name_tag else None

    # Position and team
    position_team_tag = soup.find("div", id="ctl00_phContent_dPlayerAttr").find("span", class_="pa-pos-col")
    player_bio_data["position_team"] = position_team_tag.get_text(strip=True) if position_team_tag else None

    # Height / Weight / Update
    attr_sub = soup.find("div", id="ctl00_phContent_dPlayerAttrSub")
    player_bio_data["physical_stats"] = attr_sub.get_text(strip=True) if attr_sub else None

    # Hometown, High School
    hometown_tag = soup.find("div", id="ctl00_phContent_dPlayerAttrSub2")
    player_bio_data["hometown_highschool"] = hometown_tag.get_text(strip=True) if hometown_tag else None

    # Transfer schools (hardcoded section)
    if "Transfer Schools:" in soup.text:
        transfer_index = soup.text.index("Transfer Schools:")
        transfer_text = soup.text[transfer_index:transfer_index+100].split("\n")[0]
        player_bio_data["transfer_schools"] = transfer_text.replace("Transfer Schools:", "").strip()

    career_stats_headers, game_stats_headers = determine_ourlads_headers_by_position(position=position)
    player_bio_data["position_name"] = position
    ### 2. CAREER STATS SECTION (Updated)
    career_stats = []
    career_stats_div = soup.find("div", id="ctl00_phContent_dCareerStats")
    if career_stats_div:
        table = career_stats_div.find("table")
        if table:
            # Extract headers
            thead = table.find("thead", id="ctl00_phContent_stat_career_thead")
            if thead and not career_stats_headers:
                header_cells = thead.find_all("th")
                career_stats_headers = [th.get_text(strip=True) for th in header_cells]
            tbody = table.find("tbody", id="ctl00_phContent_stat_career_tbody")
            if tbody:
                rows = tbody.find_all("tr", class_=["row-dc-wht", "row-dc-grey"])
                for row in rows:
                    cells = [td.get_text(strip=True) for td in row.find_all("td")]
                    if cells:
                        career_stats.append(dict(zip(career_stats_headers, cells)))

    ### 3. PER-GAME STATS SECTION
    game_stats = []
    game_stats_div = soup.find("div", id="ctl00_phContent_dGameStats")
    if game_stats_div:
        table = game_stats_div.find("table")
        if table:
            # Extract headers
            thead = table.find("thead", id="ctl00_phContent_stat_game_thead")
            if thead and not game_stats_headers:
                header_cells = thead.find_all("th")
                game_stats_headers = [th.get_text(strip=True) for th in header_cells]
            for row in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in row.find_all("td")]
                if cells:
                    game_stats.append(dict(zip(game_stats_headers, cells)))


    ### 4. PLAYER LINKS SECTION (like "Bio")
    player_links = []
    player_links_div = soup.find("div", id="ctl00_phContent_dPlayerLinks")
    if player_links_div:
        table = player_links_div.find("table")
        if table:
            for row in table.find_all("tr")[1:]:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    link_tag = cells[0].find("a")
                    if link_tag:
                        player_links.append({
                            "link_text": link_tag.get_text(strip=True),
                            "description": cells[1].get_text(strip=True),
                            "href": link_tag.get("href")
                        })

    return {
        "bio": player_bio_data,
        "career_stats": career_stats,
        "game_stats": game_stats,
        "player_links": player_links
    }

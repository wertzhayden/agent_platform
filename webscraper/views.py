from bs4 import BeautifulSoup
import requests
from rest_framework import viewsets
from rest_framework.response import Response


class WebScrapePlayerStats(viewsets.ViewSet):
    """
    Web Scrape Team and Player Stats from the Ourlads website. 
    """
    def list(self, request):
        return Response(retrieve_player_college_and_high_school_summary(player_link_to_school_site="https://rolltide.com/sports/football/roster/isaiah-horton/13869"))

def retrieve_schools_players_by_depth_chart(school: str) -> dict:
        """Given a school name like "alabama", fetches and parses the depth chart from ourlads.com.
        Args:
            school (str): The name of the school to fetch the depth chart for.
        Returns:
            dict: A dictionary containing players grouped by position.
        """
        if not school:
            return {"error": "School name is required."}
        results = []
        school = school or "alabama"
        url = f"https://www.ourlads.com/ncaa-football-depth-charts/depth-chart/{school}/89923"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        tbody = soup.find("tbody", id="ctl00_phContent_dcTBody")

        if tbody:
            rows = tbody.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if not cells:
                    continue

                pos = cells[0].get_text(strip=True)
                players = []

                for i in range(1, len(cells), 2):
                    player_details, stats_tables = {}, []
                    number = cells[i].get_text(strip=True)
                    player_cell = cells[i + 1] if i + 1 < len(cells) else None
                    player_name = player_cell.get_text(strip=True) if player_cell else ""
                    player_link = player_cell.find("a")["href"] if player_cell and player_cell.find("a") else ""

                    # Use the Player Link to retrieve player details and stats

                    players.append({
                        "number": number,
                        "name": player_name,
                        "position": pos,
                        "team": school,
                        "url": player_link,
                        "bio": player_details,
                        "stats": stats_tables
                    })

                results.append({
                    "position": pos,
                    "players": players
                })

        return {"players_by_position": results}



def retrieve_player_stats(player_link: str):
    """
    Given a relative player_link like 'https://www.ourlads.com/ncaa-football-depth-charts/player/isaiah-horton/157217',
    fetches and parses player bio and stats including:
      - Player bio (name, position, school, height, weight, etc.)
      - Career stats
      - Game-by-game stats
      - Player links (like Bio)
    """
    if not player_link:
        return {"error": "An Ourlads URL for the Player is required."}
    career_stats_headers = ["Season", "Rec", "Yards", "Yards per Catch", "TD", "Rushes", "Rush Yds", "Rush Avg", "TD", "Fumbles", "Lost Fumbles"]
    game_stats_headers = ["Date", "Played Against", "Rec","Yards", "Yards per Catch", "TD", "Rushes", "Rush Yds", "Rush Avg", "TD", "Fumbles", "Lost Fumbles"]
    response = requests.get(player_link)
    soup = BeautifulSoup(response.content, 'html.parser')

    ### 1. PLAYER BIO SECTION
    player_bio_data = {}
    bio_div = soup.find("div", id="ctl00_phContent_dPlayerNav")
    if bio_div:
        bio_card = bio_div.find_next("div", class_="player-div")  # top section
        if bio_card:
            name_tag = bio_card.find("h2")
            sub_header = name_tag.find_next_sibling("div") if name_tag else None
            info_lines = bio_card.stripped_strings
            for line in info_lines:
                if ':' in line:
                    key, value = line.split(":", 1)
                    player_bio_data[key.strip()] = value.strip()


    ### 2. CAREER STATS SECTION (Updated)
    career_stats = []
    career_stats_div = soup.find("div", id="ctl00_phContent_dCareerStats")
    if career_stats_div:
        table = career_stats_div.find("table")
        if table:
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


def retrieve_player_college_and_high_school_summary(player_link_to_school_site: str) -> dict:
    """
    Given a player link like 'https://rolltide.com/sports/football/roster/isaiah-horton/13869',
    fetches and parses player profile photo, info, and bio paragraphs.
    """
    response = requests.get(player_link_to_school_site)
    soup = BeautifulSoup(response.content, 'html.parser')

    result = {}

    # 1. PLAYER NAME AND PHOTO URL
    content_div = soup.find("div", class_="c-rosterpage__content")
    if content_div:
        # Find image
        img_div = content_div.find("div", class_="c-rosterbio__player-image")
        img_tag = img_div.find("img") if img_div else None
        result["photo_url"] = img_tag.get("src") if img_tag else None

        # Find name
        name_tag = content_div.find("h1")
        result["name"] = name_tag.get_text(strip=True) if name_tag else None

    # 2. PLAYER INFO (Position, Height, Weight, Class, etc.)
    player_details = {}
    details_div = content_div.find("div", class_="c-rosterpage__player-details") if content_div else None
    if details_div:
        for detail in details_div.find_all("div", recursive=False):
            spans = detail.find_all("span")
            if len(spans) == 2:
                key = spans[0].get_text(strip=True).rstrip(":")
                value = spans[1].get_text(strip=True)
                player_details[key] = value
    result["player_details"] = player_details

    # 3. BIO SECTIONS (Headers and Paragraphs)
    bio_sections = []
    tabs_div = soup.find("div", class_="c-rosterpage__tabs")
    if tabs_div:
        prose_div = tabs_div.find("div", class_="legacy_to_nextgen s-text-paragraph--longform sidearm_prose text-theme-safe overflow-auto")
        if prose_div:
            headers = prose_div.find_all("h2")
            for header in headers:
                section_title = header.get_text(strip=True)
                next_p = header.find_next_sibling("p")
                paragraph_text = next_p.get_text(strip=True) if next_p else ""
                bio_sections.append({
                    "header": section_title,
                    "paragraph": paragraph_text
                })

    result["bio_sections"] = bio_sections

    return result

import requests
from bs4 import BeautifulSoup


def retrieve_schools_players_by_depth_chart(school: str, school_id: int) -> dict:
        """Given a school name like "alabama", fetches and parses the depth chart from ourlads.com.
        Args:
            school (str): The name of the school to fetch the depth chart for.
        Returns:
            dict: A dictionary containing players grouped by position.
        """
        if not school:
            return {"error": "School name is required."}
        if not school_id:
            return {"error": "School ID by Ourlads is required."}
        results = []
        school = school or "alabama"
        url = f"https://www.ourlads.com/ncaa-football-depth-charts/depth-chart/{school}/{school_id}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Map tbody IDs to sides of the ball
        tbody_map = {
            "ctl00_phContent_dcTBody": "Offense",
            "ctl00_phContent_dcTBody2": "Defense",
            "ctl00_phContent_dcTBody3": "Special Teams"
        }

        for tbody_id, side_of_ball in tbody_map.items():
            tbody = soup.find("tbody", id=tbody_id)
            if not tbody:
                continue

            rows = tbody.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if not cells:
                    continue

                pos = cells[0].get_text(strip=True)
                players = []

                for i in range(1, len(cells), 2):
                    number = cells[i].get_text(strip=True)
                    player_cell = cells[i + 1] if i + 1 < len(cells) else None
                    player_name = player_cell.get_text(strip=True) if player_cell else ""
                    player_link = player_cell.find("a")["href"] if player_cell and player_cell.find("a") else ""
                    if player_name:
                        players.append({
                            "number": number,
                            "name": player_name,
                            "position": pos,
                            "side_of_the_ball": side_of_ball,
                            "team": school,
                            "url": player_link,
                        })

                results.append({
                    "position": pos,
                    "players": players
                })

        return results

import re
import requests
from bs4 import BeautifulSoup

from rest_framework import viewsets
from rest_framework.response import Response

from core.models.active_nfl_players import ActiveNFLPlayers


class IngestActiveNFLPlayerContractDetails(viewsets.ViewSet):
    """
    Web Scrape Team and Player Stats from the Ourlads website. 
    """
    def create(self, request):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        player_spot_trac_id = request.data.get("spot_trac_id")
        if not first_name or not last_name or not player_spot_trac_id:
            return Response({"error": "Missing required parameters: first_name, last_name, player_spot_trac_id"}, status=400)
        contract_details = retrieve_player_contract_details(first_name=first_name, last_name=last_name, player_spot_trac_id=player_spot_trac_id)
        # update_active_player = update_active_nfl_player_contract_details(contract_details=contract_details)
        player_bio_data = contract_details.get("bio", {})
        age = player_bio_data.get("age", None)
        experience = player_bio_data.get("experience", None)
        agents_firm = player_bio_data.get("agents", {}).get("firm", None)
        agents = player_bio_data.get("agents", {}).get("agent", [])
        contract_info = contract_details.get("contract_info", {})
        cap_hit = contract_info.get("2025_cap_hit", None)
        cash_this_year = contract_info.get("2025_cash", None)
        career_earnings = contract_info.get("career_earnings", None)
        active_players = ActiveNFLPlayers.objects.filter(first_name=first_name, last_name=last_name).first()
        active_players.age = age
        active_players.years_of_experience = experience
        active_players.firm = agents_firm
        active_players.agents = agents
        active_players.current_cap_hit = cap_hit
        active_players.current_year_cash_salary = cash_this_year
        active_players.career_earnings = career_earnings
        active_players.spot_trac_id = player_spot_trac_id
        active_players.save()

        return Response(contract_details)

    
def update_active_nfl_player_contract_details(contract_details: dict) -> dict:
    """Updated the Player from the ActiveNFLPlayers models with the Contract Details from Spotrac"""
    #TODO: Consolidate the Create ViewSet Logic into this Function
    return contract_details
 

def retrieve_player_contract_details(first_name: str, last_name: str, player_spot_trac_id: int) -> dict:
        """
        Retrieve the Contract Details of an NFL Player from Spotrac
        
        Example URL: https://www.spotrac.com/nfl/player/_/id/21796/dalvin-tomlinson
        """

        url = f"https://www.spotrac.com/nfl/player/_/id/{player_spot_trac_id}/{first_name}-{last_name}"
        # response = requests.get("https://www.spotrac.com/nfl/player/_/id/21796/dalvin-tomlinson")
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })
        soup = BeautifulSoup(response.content, 'html.parser')
        player_bio_data, contract_data = {}, {}

        ## 1. BIO SECTION LOOP
        bio_divs = soup.find_all("div", class_="col-md-12 text-white")
        for div in bio_divs:
            strong_tag = div.find("strong")
            span_tag = div.find("span", class_="text-yellow")
            if strong_tag and span_tag:
                label = strong_tag.get_text(strip=True).rstrip(":").lower()
                value = span_tag.get_text(strip=True)

                # Age → float years
                if label == "age":
                    match = re.search(r"(\d+)y-(\d+)m", value)
                    if match:
                        years = int(match.group(1))
                        months = int(match.group(2))
                        value = round(years + months / 12, 2)

                # Experience → int
                elif label == "exp":
                    label = "experience"
                    match = re.search(r"(\d+)", value)
                    value = int(match.group(1)) if match else None

                # Drafted → dict
                elif label == "drafted":
                    match = re.search(r"Round\s+(\d+)\s+\(#(\d+)\s+overall\),\s+(\d{4})", value)
                    if match:
                        value = {
                            "round": int(match.group(1)),
                            "overall_pick": int(match.group(2)),
                            "year": int(match.group(3))
                        }

                    label = "draft"

                # Agents → dict
                elif "agent" in label:
                    agents_list = [a.strip() for a in value.split(",") if a.strip()]
                    firm_match = re.search(r"\((.*?)\)$", agents_list[-1]) if agents_list else None
                    firm = firm_match.group(1) if firm_match else None
                    agents_cleaned = [re.sub(r"\s*\(.*?\)$", "", a).strip() for a in agents_list]
                    value = {
                        "firm": firm,
                        "agent": agents_cleaned
                    }
                    label = "agents"

                player_bio_data[label] = value

        
        bubble_divs = soup.find_all("div", class_="col-md-4 col-sm-6 bubble-item")
        for bubble in bubble_divs:
            title_tag = bubble.find("h5", class_="card-title text-darkgrey text-white text-uppercase py-2 text-center fs-sm bg-darkgrey")
            value_tag = bubble.find("p", class_="card-text text-center text-black fs-lg fw-normal pb-2")
            if title_tag and value_tag:
                # Convert title to snake_case key
                raw_title = title_tag.get_text(strip=True)
                key = re.sub(r'[^0-9a-zA-Z]+', '_', raw_title).lower().strip('_')

                # Convert $ value to int (remove $ and commas)
                raw_value = value_tag.get_text(strip=True)
                num_value = re.sub(r"[^\d]", "", raw_value)
                value = int(num_value) if num_value else 0

                contract_data[key] = value

        return {
            "bio": player_bio_data,
            "contract_info": contract_data,
        }
        
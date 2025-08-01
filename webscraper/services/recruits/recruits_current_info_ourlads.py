import time
import random
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from core.models.player import Player

from webscraper.models.recruit import Recruit
from webscraper.services.player_hs_rankings.retrieve_latest_school_by_player import retrieve_latest_school_by_player
from webscraper.utils.webscraper_utils import remove_suffix_from_end_of_name

def safe_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def retrieve_recruits_current_info_via_ourlads(school_name: str = None,number_of_recruits: int = None) -> list:
    """Retrieve current recruit info in a single browser session."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    rank_not_found = "N/A"

    if school_name:
        recruits = Recruit.objects.filter(recruiting_class__school__external_name__iexact=school_name)[:]
    elif number_of_recruits:
        recruits = Recruit.objects.all()[:number_of_recruits]
    else:
        recruits = Recruit.objects.all()
    recruits_list = []

    for recruit in recruits:
        url = recruit.school_link
        try:
            player = Player.objects.filter(
                first_name__icontains=remove_suffix_from_end_of_name(recruit.first_name),
                last_name__icontains=remove_suffix_from_end_of_name(recruit.last_name),
            ).first()
            data = retrieve_latest_school_by_player(url=url, driver=driver)
        #     {
        #     "transfer": {
        #         "rating": "90",
        #         "stars": 4,
        #         "ranks": {
        #             "OVR": "160",
        #             "S": "6"
        #         }
        #     },
        #     "prospect": {
        #         "rating": "93",
        #         "stars": 4,
        #         "ranks": {
        #             "NATL.": "154",
        #             "CB": "12",
        #             "OH": "6"
        #         }
        #     },
        #     "num_rankings_blocks": 2
        # }

            transfer_ranks = list(data.get("transfer", {}).get("ranks", {}).values())
            hs_ranks = list(data.get("prospect", {}).get("ranks", {}).values())
            transfer_stars = data.get("transfer", {}).get("stars")
            prospect_stars = data.get("prospect", {}).get("stars")
            transfer_rating = data.get("transfer", {}).get("rating")
            prospect_rating = data.get("prospect", {}).get("rating")

            # Split the City & State
            city_state = data.get("city").split(",") if data.get("city") else []
            city = city_state[0].strip() if len(city_state) > 0 else None
            state = city_state[1].strip() if len(city_state) > 1 else None
            
            recruit.current_position = data.get("position")
            recruit.current_height = data.get("height")
            recruit.current_weight = data.get("weight") if data.get("weight") and data.get("weight").isdigit() else None
            recruit.experience_level_at_current_school = data.get("exp")
            recruit.current_school = data.get("current_school")
            recruit.player = player
            recruit.jersey_number = int(''.join(filter(str.isdigit, data.get("jersey")))) if data.get("jersey") and any(char.isdigit() for char in data.get("jersey")) else None
            recruit.stars = prospect_stars
            recruit.hs_rating_score = safe_float(prospect_rating)
            recruit.high_school = data.get("high_school")
            recruit.hometown_city = city
            recruit.hometown_state = state
            recruit.national_rank = hs_ranks[0] if len(hs_ranks) > 0 and hs_ranks[0] not in rank_not_found else None
            recruit.position_rank = hs_ranks[1] if len(hs_ranks) > 1 and hs_ranks[1] not in rank_not_found else None
            recruit.state_rank = hs_ranks[2] if len(hs_ranks) > 2 and hs_ranks[2] not in rank_not_found else None
            # 247Sports does not have this info on Transfers in the Commit List
            recruit.transfer_stars = transfer_stars
            recruit.transfer_rating_score = safe_float(transfer_rating)
            recruit.transfer_national_rank = transfer_ranks[0] if len(transfer_ranks) > 0 and transfer_ranks[0] not in rank_not_found else None
            recruit.transfer_position_rank = transfer_ranks[1] if len(transfer_ranks) > 1 and transfer_ranks[1] not in rank_not_found else None
            recruit.transfer_state_rank = transfer_ranks[2] if len(transfer_ranks) > 2 and transfer_ranks[2] not in rank_not_found else None
            recruit.save()

            recruits_list.append({
                "first_name": recruit.first_name,
                "last_name": recruit.last_name,
                "player_first": player.first_name if player else None,
                "player_last": player.last_name if player else None,
                "jersey": recruit.jersey_number,
                "high_school": recruit.high_school,
                "hometown_city": recruit.hometown_city,
                "hometown_state": recruit.hometown_state,
                "stars": recruit.stars,
                "hs_rating_score": recruit.hs_rating_score,
                "national_rank": recruit.national_rank,
                "position_rank": recruit.position_rank,
                "state_rank": recruit.state_rank,
                "transfer_stars": recruit.transfer_stars,
                "transfer_rating_score": recruit.transfer_rating_score,
                "transfer_national_rank": recruit.transfer_national_rank,
                "transfer_position_rank": recruit.transfer_position_rank,
                "transfer_state_rank": recruit.transfer_state_rank,
                "position": recruit.current_position,
                "height": recruit.current_height,
                "weight": recruit.current_weight,
                "experience_level_at_current_school": recruit.experience_level_at_current_school,
                "current_school": recruit.current_school,
                "school_link": recruit.school_link
            })
        except Exception as e:
            return f"Failed to process {url}: {e}"

        time.sleep(random.uniform(1, 2))  # Backoff between requests

    driver.quit()
    return recruits_list

def retrieve_latest_school_by_player(url: str, driver) -> dict:
    if not url:
        return {}

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "header.profile-header"))
        )
    except (TimeoutException, WebDriverException) as e:
        return {}

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    result = {
        "name": None, "position": None, "height": None, "weight": None,
        "high_school": None, "city": None, "exp": None, "current_school": None,
        "jersey": None, "class": None, "age": None, "is_transfer": None,
        "transfer_rating": None, "transfer_position_rank": None, "transfer_ovr_rank": None,
        "prospect_rating": None, "prospect_position_rank": None, "prospect_ovr_rank": None,
        "transfer_stars": None, "prospect_stars": None, "transfer_state_rank": None, "prospect_state_rank": None,
        "transfer": {}, "prospect": {}, "num_rankings_blocks": 0,
    }

    header = soup.find("header", class_="profile-header")
    if header:
        name_div = header.find("h1", class_="name")
        if name_div:
            result["name"] = name_div.text.strip()

        metrics = header.find("ul", class_="metrics-list")
        if metrics:
            for li in metrics.find_all("li"):
                label = li.find("span")
                val = label.find_next_sibling("span") if label else None
                if not val:
                    continue
                key = label.text.strip().lower()
                if key == "pos":
                    result["position"] = val.text.strip()
                elif key == "height":
                    result["height"] = val.text.strip()
                elif key == "weight":
                    result["weight"] = val.text.strip()

        details = header.find("ul", class_="details")
        if details:
            for li in details.find_all("li"):
                label = li.find("span")
                val = li.get_text(strip=True).replace(label.text, "").strip() if label else None
                key = label.text.strip().lower() if label else ""
                if "high school" in key:
                    result["high_school"] = val
                elif "city" in key:
                    result["city"] = val
                elif "exp" in key:
                    result["exp"] = val

    team_block = soup.find("section", class_="team-block")
    if team_block:
        school = team_block.find("h2")
        result["current_school"] = school.text.strip() if school else None

        logo = team_block.find("img")
        result["school_logo_url"] = logo["src"] if logo and logo.has_attr("src") else None

        vitals = team_block.find("ul", class_="vitals")
        if vitals:
            for li in vitals.find_all("li"):
                label = li.find("span")
                val = label.find_next_sibling("span") if label else None
                key = label.text.strip().lower() if label else ""
                if "jersey" in key:
                    result["jersey"] = val.text.strip()
                elif "class" in key:
                    result["class"] = val.text.strip()
                elif "age" in key:
                    result["age"] = val.text.strip()

    # Get the Player's HS & Transfer Rankings by Star & Rank
    section = soup.select_one("section.as-a-prospect")
    if section:
        ranking_blocks = section.select("div.body.rankings")
        result["num_rankings_blocks"] = len(ranking_blocks)

        for block in ranking_blocks:
            title_el = block.select_one("h3.title")
            title_text = title_el.get_text(strip=True) if title_el else ""

            # Get rating
            score_el = block.select_one("div.rank-block")
            rating = score_el.get_text(strip=True) if score_el else None

            # Count stars
            stars = len(block.select("div.stars-block span.icon-starsolid.yellow"))

            # Extract ranks
            rank_items = block.select("ul.ranks-list li")
            ranks = {}
            for li in rank_items:
                label_el = li.select_one("b")
                value_el = li.select_one("strong")
                if label_el and value_el:
                    label = label_el.get_text(strip=True)
                    value = value_el.get_text(strip=True)
                    ranks[label] = value

            # Store by type
            if title_text == "247Sports Transfer Rankings":
                result["transfer"] = {
                    "rating": rating,
                    "stars": stars,
                    "ranks": ranks
                }
            elif title_text == "247Sports":
                result["prospect"] = {
                    "rating": rating,
                    "stars": stars,
                    "ranks": ranks
                }
    return result

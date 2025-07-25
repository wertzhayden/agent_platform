"""Retrieve the Latest School that is associated with a Player via 247Sports"""

from bs4 import BeautifulSoup
from webscraper.services.player_data.retrieve_team_depth_chart import retrieve_schools_players_by_depth_chart
from webscraper.services.player_data.retrieve_player_stats import retrieve_player_stats
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import re

def retrieve_latest_school_by_player(url: str) -> dict:
    """
    Retrieve Latest School by Player from 247Sports 
    Example: https://247sports.com/Player/julian-sayin-46102486/

    """
    if not url:
        return {}
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    header = soup.find("header", class_="profile-header")
    if not header:
        return {}

    result = {
        "name": None,
        "position": None,
        "height": None,
        "weight": None,
        "high_school": None,
        "city": None,
        "exp": None,
        "current_school": None,
        "jersey": None,
        "class": None,
        "age": None,
        "transfer_rating": None,
        "transfer_position_rank": None,
        "transfer_ovr_rank": None,
    }

    header = soup.find("header", class_="profile-header")
    if header:
        name_div = header.find("h1", class_="name")
        if name_div:
            result["name"] = name_div.text.strip()

        metrics = header.find("ul", class_="metrics-list")
        if metrics:
            items = metrics.find_all("li")
            for li in items:
                label = li.find("span")
                val = label.find_next_sibling("span") if label else None
                if not val:
                    continue
                text = label.text.strip().lower()
                if text == "pos":
                    result["position"] = val.text.strip()
                elif text == "height":
                    result["height"] = val.text.strip()
                elif text == "weight":
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

    # ------ School Info (Lower Cards) ------
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
                text = label.text.strip().lower() if label else ""
                if "jersey" in text:
                    result["jersey"] = val.text.strip()
                elif "class" in text:
                    result["class"] = val.text.strip()
                elif "age" in text:
                    result["age"] = val.text.strip()

    # ------ Transfer Rating from First '.body.rankings' ------
    transfer_div = soup.select_one("div.body.rankings")

    if transfer_div:
        stars = len(transfer_div.select("div.stars-block span.icon-starsolid.yellow"))

        score_div = transfer_div.select_one("div.rank-block")
        score_val = score_div.get_text(strip=True) if score_div else None

        rank_items = transfer_div.select("ul.ranks-list li strong")
        ranks = [r.get_text(strip=True) for r in rank_items]

        result["transfer_rating"] = score_val
        result["transfer_stars"] = stars
        if len(ranks) >= 2:
            result["transfer_ovr_rank"] = ranks[0]
            result["transfer_position_rank"] = ranks[1]


    return result
from rest_framework import viewsets
from rest_framework.response import Response

from webscraper.models.recruit import Recruit
from webscraper.services.player_hs_rankings.retrieve_latest_school_by_player import retrieve_latest_school_by_player


import time
import random
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from webscraper.models.recruit import Recruit



class IngestRecruitsCurrentData(viewsets.ViewSet):
    """
    Web Scrape Team and Player Stats from the Ourlads website. 
    """

    def create(self, request):
        # MAX_WORKERS = 5  # Adjust as needed for performance

        return Response(retrieve_recruits_current_info_via_ourlads())

def retrieve_recruits_current_info_via_ourlads(number_of_recruits: int = None) -> list:
    """Retrieve current recruit info in a single browser session."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    recruits = Recruit.objects.all()
    recruits_list = []

    for recruit in recruits:
        url = recruit.school_link
        try:
            data = retrieve_latest_school_by_playerr(url=url, driver=driver)
            recruit.current_position = data.get("position")
            recruit.current_height = data.get("height")
            recruit.current_weight = data.get("weight") if data.get("weight").isdigit() else None
            recruit.experience_level_at_current_school = data.get("exp")
            recruit.current_school = data.get("current_school")
            recruit.save()

            recruits_list.append({
                "first_name": recruit.first_name,
                "last_name": recruit.last_name,
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

def retrieve_latest_school_by_playerr(url: str, driver) -> dict:
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
        "jersey": None, "class": None, "age": None,
        "transfer_rating": None, "transfer_position_rank": None, "transfer_ovr_rank": None,
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

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import re

def retrieve_player_hs_rankings(school: str, year: int = 2025) -> dict:
    """
    Retrieve High School Rankings by Team & Year 
    Example: https://247sports.com/college/alabama/Season/2025-Football/Commits/

    """
    url = f"https://247sports.com/college/{school}/season/{year}-football/commits/"

    options = webdriver.ChromeOptions()
    # Uncomment for headless scraping
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    result = {
        "ranks": {},
        "players": [],
        "transfers": []
    }

    # ---------------- RANKS ----------------
    main_div = soup.find("div", class_="ri-page__main")
    if not main_div:
        return result

    rank_blocks = main_div.find_all("div", class_="ir-bar__ranks")
    for rank_div in rank_blocks:
        title_tag = rank_div.find("h3")
        value_tag = rank_div.find("span", class_="ir-bar__number")
        if title_tag and value_tag:
            key = title_tag.text.strip().lower().replace(" ", "_")
            result["ranks"][key] = {
                "title": title_tag.text.strip(),
                "value": value_tag.text.strip()
            }

    # ---------------- COMMITS ----------------
    commit_list = main_div.find("ul", class_="ri-page__list")
    if commit_list:
        for li in commit_list.find_all("li", class_="ri-page__list-item"):
            player_data = {}

            name_link = li.find("a", class_="ri-page__name-link")
            player_data["name"] = name_link.text.strip() if name_link else None
            player_data["profile_url"] = name_link["href"] if name_link else None

            meta_span = li.find("span", class_="meta")
            player_data["school_location"] = meta_span.text.strip() if meta_span else None

            pos_div = li.find("div", class_="position")
            player_data["position"] = pos_div.text.strip() if pos_div else None

            metrics_div = li.find("div", class_="metrics")
            player_data["ht_wt"] = metrics_div.text.strip() if metrics_div else None

            star_score_div = li.find("div", class_="ri-page__star-and-score")
            if star_score_div:
                stars = star_score_div.find_all("span", class_="icon-starsolid yellow")
                player_data["stars"] = len(stars)
                score_span = star_score_div.find("span", class_="score")
                player_data["rating_score"] = score_span.text.strip() if score_span else None
            else:
                player_data["stars"] = 0
                player_data["rating_score"] = None

            rank_div = li.find("div", class_="rank")
            if rank_div:
                rank_links = rank_div.find_all("a")
                if len(rank_links) >= 3:
                    player_data["national_rank"] = rank_links[0].text.strip()
                    player_data["position_rank"] = rank_links[1].text.strip()
                    player_data["state_rank"] = rank_links[2].text.strip()

            status_div = li.find("div", class_="status")
            if status_div:
                status_text = status_div.find("p", class_="commit-date")
                player_data["status"] = status_text.text.strip() if status_text else None

            result["players"].append(player_data)

    # ---------------- TRANSFERS ----------------
    transfer_list = soup.find_all("li", class_="portal-list_itm")
    for li in transfer_list:
        transfer = {}

        player_block = li.find("div", class_="player")
        if player_block:
            link = player_block.find("a")
            transfer["name"] = link.text.strip() if link else None
            transfer["profile_url"] = link["href"] if link else None

        # details_ul = li.find("ul", class_="details ")
        # if details_ul:
        #     for detail_item in details_ul.find_all("li"):
        #         label_spans = detail_item.find_all("span")
        #         if len(label_spans) >= 2:
        #             label = label_spans[0].text.strip().lower()
        #             value = label_spans[1].text.strip()
        #             if label == "high school":
        #                 transfer["high_school"] = value
        #             elif label == "city":
        #                 transfer["school_location"] = value  # reuse key used for high school players
        #             elif label == "exp":
        #                 transfer["exp"] = value

        metrics = li.find("div", class_="metrics")
        transfer["ht_wt"] = metrics.text.strip() if metrics else None

        position = li.find("div", class_="position")
        transfer["position"] = position.text.strip() if position else None

        eligibility = li.find("div", class_="eligibility")
        transfer["eligibility"] = eligibility.text.strip() if eligibility else None

        transfer["transfer_from"] = None  # default

        transfer_school = li.find("div", class_="transfer-institution")
        if transfer_school:
            transfer_links = transfer_school.find_all("a")
            if len(transfer_links) == 2:
                from_img = transfer_links[0].find("img")
                if from_img and from_img.has_attr("alt"):
                    transfer["transfer_from"] = from_img["alt"].strip()



        transfer["ratings"] = []  # new structure for multiple ratings

        rating_div = li.find("div", class_="rating")
        if rating_div:
            for rating_block in rating_div.find_all("span", recursive=False):
                stars = rating_block.find_all("span", class_="icon-starsolid yellow")
                score_span = rating_block.find("span", class_="score")
                level_span = rating_block.find("span", class_="level")
                level = level_span.text.strip("() ") if level_span else None


                rating = {
                    "stars": len(stars),
                    "rating_score": re.sub(r"[^\d.]", "", score_span.text) if score_span else None,
                    "level": "Transfer" if level == "T" else level
                }

                transfer["ratings"].append(rating)


        result["transfers"].append(transfer)

    return result
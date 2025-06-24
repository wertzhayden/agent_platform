import requests
from bs4 import BeautifulSoup

# @TODO: Update the Code to Extract from the Roll Tide website. 
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
        # img_div = content_div.find("div", class_="c-rosterbio__player-image")
        # img_tag = img_div.find("img") if img_div else None
        # result["photo_url"] = img_tag.get("src") if img_tag else None
        img_tag = content_div.find("img", attrs={"data-test-id": "s-image-resized_img"})
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

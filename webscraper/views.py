from bs4 import BeautifulSoup
import requests
from rest_framework import viewsets
from rest_framework.response import Response
from webscraper.services.player_data.retrieve_team_depth_chart import retrieve_schools_players_by_depth_chart
from webscraper.services.player_data.retrieve_player_stats import retrieve_player_stats
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from webscraper.services.player_hs_rankings.retrieve_hs_rankings import retrieve_player_hs_rankings
from webscraper.services.player_hs_rankings.retrieve_latest_school_by_player import retrieve_latest_school_by_player


class WebScrapePlayerStats(viewsets.ViewSet):
    """
    Web Scrape Team and Player Stats from the Ourlads website. 
    """
    def list(self, request):
        # return Response(retrieve_player_stats(position=request.data.get("position"), player_link=request.data.get("player_link")))
        # return Response(retrieve_schools_players_by_depth_chart(school=request.data.get("school"), school_id=request.data.get("school_id")))
        # return Response(retrieve_player_hs_rankings(school=request.data.get("school"), year=request.data.get("year")))
        return Response(retrieve_latest_school_by_player(url=request.data.get("url")))

"""
Remaining Lists to Scrape:

1. PFF Freshman All-American List - COMPLETE
2. PWAA Freshman All-American List - COMPLETE
3. 247sports Freshman All-American List - COMPLETE
4. College Football News (CFN) Freshman All-American List - COMPLETE
5. on3 Freshman All-American List - COMPLETE
6. Freshman ALL-SEC List - COMPLETE 
7. CFN All-AAC List - COMPLETE
8. CFN All-ACC List - COMPLETE
7. CFN All-Big-10 List - COMPLETE
9. CFN All-Big-12 List - ...
10. CFN All-CUSA List -
11. CFN All-MAC List -
12. CFN All-MWC List -
13. CFN All-Pac-12 List -
14. CFN All-SEC List -
15. CFN All-Sun-Belt List -
16. Shawn Alexander Freshman Semi-Finalists List - 
17. ...
"""
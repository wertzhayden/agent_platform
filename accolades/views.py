from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from accolades.accolade_data_lists.all_freshman_lists.two_four_seven_sports import TWO_FOUR_SEVEN_SPORTS

class IngestAccoladesViewset(viewsets.ViewSet):
    """
    Web Scrape Team and Player Stats from the Ourlads website. 
    """

    def list(self, request):
        twenty_four_seven_sports_all_freshman_list = TWO_FOUR_SEVEN_SPORTS.get("two_four_seven_sports", [])
        return Response(twenty_four_seven_sports_all_freshman_list)

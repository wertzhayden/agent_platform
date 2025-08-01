from rest_framework import viewsets
from rest_framework.response import Response

from webscraper.services.recruits.recruits_current_info_ourlads import retrieve_recruits_current_info_via_ourlads

class IngestRecruitsCurrentData(viewsets.ViewSet):
    """
    Web Scrape Team and Player Stats from the Ourlads website. 
    """

    def create(self, request):
        # MAX_WORKERS = 5  # Adjust as needed for performance
        """Ingest current recruit data via Ourlads."""
        if request.data.get("school"):
            return Response(retrieve_recruits_current_info_via_ourlads(school_name=request.data.get("school")))
        if request.data.get("number_of_recruits"):
            return Response(retrieve_recruits_current_info_via_ourlads(number_of_recruits=request.data.get("number_of_recruits")))
        return Response(retrieve_recruits_current_info_via_ourlads())

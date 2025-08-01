from rest_framework import viewsets
from rest_framework.response import Response

from webscraper.constants.ourlads_constants import TEAM_IDS
from webscraper.services.recruits.recruits_by_school_and_year import get_recruits_by_school_and_year
    
class RecruitsBySchoolAndYear(viewsets.ViewSet):
    """
    View to retrieve HS recruits across schools and years using 247Sports
    """

    def create(self, request):
        # MAX_WORKERS = 5  # Adjust as needed for performance
        recruits = []
        years = [2021, 2022, 2023, 2024, 2025]
        school = request.data.get("school")
        year = request.data.get("year") or years

        # Normalize to a list of years
        if isinstance(year, str):
            year = [int(year)]
        elif isinstance(year, list):
            year = [int(y) for y in year]
        else:
            year = years

        if school:
            for y in year:
                data = get_recruits_by_school_and_year(school_name=school, year=int(y))
                recruits.append(data)
            return Response(recruits)

        for team in TEAM_IDS:
            for yr in years:
                recruit_data = get_recruits_by_school_and_year(school_name=team, year=yr)
                recruits.append(recruit_data)

        return Response(recruits)

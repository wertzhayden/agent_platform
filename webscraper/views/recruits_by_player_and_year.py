from rest_framework import viewsets
from rest_framework.response import Response

from core.models.school import School
from core.utils.pull_ourlads_depth_charts_helpers import (
    split_high_school_and_hometown,
    convert_string_to_float
)

from webscraper.constants.ourlads_constants import TEAM_IDS
from webscraper.models.recruiting_class import RecruitingClass
from webscraper.models.recruit import Recruit
from webscraper.services.player_hs_rankings.retrieve_hs_rankings import retrieve_player_hs_rankings



class RecruitsBySchoolAndYear(viewsets.ViewSet):
    """
    Web Scrape Team and Player Stats from the Ourlads website. 
    """

    def create(self, request):
        recruits = []
        if request.data.get("school") and request.data.get("year"):
            recruits = get_recruits_by_school_and_year(team=request.data.get("school"), year=request.data.get("year"))
            return Response(recruits)
        years = [2021, 2022, 2023, 2024, 2025]
        for team in TEAM_IDS:
            for year in years:
                recruits.append(get_recruits_by_school_and_year(team=team,year=year))
        return Response(recruits)


def get_recruits_by_school_and_year(school: str, year: int) -> dict:
        """
        Get the high school recruits for a specific school and year.
        """
        rank_not_found = "N/A"
        school_name = school
        year = year
        school = School.objects.filter(name=school_name).first()

        hs_rankings = retrieve_player_hs_rankings(school=school_name, year=year)
        recruiting_class_rank = hs_rankings.get("ranks", {})
        # Safely extract ranks
        overall_rank = recruiting_class_rank.get("overall_rank", {}).get("value")
        transfer_rank = recruiting_class_rank.get("transfer_rank", {}).get("value")
        composite_rank = recruiting_class_rank.get("composite_rank", {}).get("value")

        recruiting_class, _ = RecruitingClass.objects.get_or_create(
            school=school,
            year=year,
            defaults={
                "overall_rank": int(overall_rank) if overall_rank not in rank_not_found else None,
                "transfer_rank": int(transfer_rank) if transfer_rank not in rank_not_found else None,
                "composite_rank": int(composite_rank) if composite_rank not in rank_not_found else None
            }
        )

        results = []

        def parse_name(full_name):
            name_parts = full_name.split(" ", 1)
            return name_parts[0], name_parts[1] if len(name_parts) > 1 else ""

        def parse_ht_wt(ht_wt):
            parts = ht_wt.split("/")
            height = parts[0].strip() if len(parts) > 0 else None
            weight = parts[1].strip() if len(parts) > 1 else None
            return height, weight

        # --- Handle Recruits ---
        for player in hs_rankings.get("players", []):
            if not player.get("name"):
                continue
            first_name, last_name = parse_name(player["name"])
            height, weight = parse_ht_wt(player.get("ht_wt", ""))
            profile_url = f"https:{player.get("profile_url")}"
            position = player.get("position", "").lower()
            stars = player.get("stars")
            hs_rating_score = player.get("rating_score")
            national_rank = int(player.get("national_rank")) if player.get("national_rank").isdigit() else None
            position_rank = int(player.get("position_rank")) if player.get("position_rank").isdigit() else None
            state_rank = int(player.get("state_rank")) if player.get("state_rank").isdigit() else None
            status = player.get("status")
            hs, city, state = split_high_school_and_hometown(player.get("school_location"))
            recruit, _ = Recruit.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                position=position,
                high_school=hs,
                hometown_city=city,
                hometown_state=state,
                recruiting_class=recruiting_class,
                defaults={
                    "height": height,
                    "weight": weight,
                    "stars": stars,
                    "hs_rating_score": round(float(hs_rating_score), 2) if hs_rating_score.isdigit() else None,
                    "national_rank": national_rank,
                    "position_rank": position_rank,
                    "state_rank": state_rank,
                    "status": status,
                    "school_link": profile_url
                }
            )
            results.append({
                "name": f"{first_name} {last_name}",
                "type": "hs",
                "id": recruit.id,
                "school_link": recruit.school_link,
                "position": position,
                "height": height,
                "weight": weight,
                "stars": stars,
                "hs_rating_score": hs_rating_score,
                "national_rank": national_rank,
                "position_rank": position_rank,
                "state_rank": state_rank,
                "status": status
            })

        # --- Handle Transfers ---
        for transfer in hs_rankings.get("transfers", []):
            if not transfer.get("name"):
                continue

            first_name, last_name = parse_name(transfer["name"])
            height, weight = parse_ht_wt(transfer.get("ht_wt", ""))
            profile_url = transfer.get("profile_url")
            position = transfer.get("position", "").lower()
            hs_stars = hs_rating_score = transfer_stars = transfer_rating_score = None
            for rating in transfer.get("ratings", []):
                level = rating.get("level", "").lower()
                if level == "transfer":
                    transfer_stars = rating.get("stars")
                    transfer_rating_score = rating.get("rating_score")
                elif level == "hs":
                    hs_stars = rating.get("stars")
                    hs_rating_score = rating.get("rating_score")
            recruit, _ = Recruit.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                position=position,
                high_school=None,
                hometown_city=None,
                hometown_state=None,
                recruiting_class=recruiting_class,
                defaults={
                    "height": height,
                    "weight": weight,
                    "stars": hs_stars,
                    "school_link": profile_url
                }
            )
            if hs_stars is not None:
                recruit.stars = hs_stars
            if hs_rating_score is not None:
                recruit.rating_score = convert_string_to_float(hs_rating_score)
            if transfer_stars is not None:
                recruit.transfer_stars = transfer_stars
            if transfer_rating_score is not None:
                recruit.transfer_rating_score = convert_string_to_float(transfer_rating_score)
            recruit.save()

            results.append({
                "name": f"{first_name} {last_name}",
                "type": "transfer",
                "id": recruit.id,
                "transfer_stars": transfer_stars,
                "transfer_rating_score": transfer_rating_score,
                "hs_stars": hs_stars,
                "hs_rating_score": hs_rating_score,
                "position": position,
                "school_link": recruit.school_link,
            })

        return {
            "recruiting_class": {
                "id": recruiting_class.id,
                "school": school_name,
                "year": year,
                "overall_rank": overall_rank,
                "transfer_rank": transfer_rank,
                "composite_rank": composite_rank
            },
            "recruits": results
        }
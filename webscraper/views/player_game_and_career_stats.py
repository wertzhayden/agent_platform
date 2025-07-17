from rest_framework import viewsets
from rest_framework.response import Response

from core.models.player import Player

from webscraper.services.player_data.retrieve_player_stats import retrieve_player_stats
from core.utils.pull_ourlads_depth_charts_helpers import (
    CAREER_STATS_SERIALIZER_MAP,
    GAME_STATS_SERIALIZER_MAP,
    determine_ourlads_position,
    convert_ourlads_height_and_weight_from_players_page,
    convert_ourlads_hometown_and_high_school,
)


class IngestPlayersGameAndCareerStats(viewsets.ViewSet):
    """
    Web Scrape Team and Player Stats from the Ourlads website. 
    """

    def create(self, request):
        return Response(retrieve_game_and_career_stats_of_all_players())

def retrieve_game_and_career_stats_of_all_players():    
        players = Player.objects.all()
        all_results = []

        for player in players:  # ✅ Loop over model instances

            # Skip special teams players
            if (player.side_of_ball or "").strip().lower() == "special teams":
                continue

            position = determine_ourlads_position(
                position=player.position,
                side_of_ball=player.side_of_ball
            )

            player_stats = retrieve_player_stats(
                player_link=player.ourlads_link,
                position=position
            )

            # Parse and assign player attributes
            height, weight = convert_ourlads_height_and_weight_from_players_page(
                ht_wt_string=player_stats.get("bio", {}).get("physical_stats")
            )
            city, state, high_school = convert_ourlads_hometown_and_high_school(
                hometown_data=player_stats.get("bio", {}).get("hometown_highschool")
            )
            schools_attended = player_stats.get("bio", {}).get("transfer_schools")

            # Ensure it's a list
            if isinstance(schools_attended, str):
                schools_attended = [schools_attended]
            elif schools_attended is None:
                schools_attended = []

            # Save to Player model
            player.height = height
            player.weight = weight
            player.hometown_city = city
            player.hometown_state = state
            player.high_school = high_school
            player.schools_attended = schools_attended
            player.save()

            # --- Save Career Stats ---
            career_stats = player_stats.get("career_stats", [])
            if not career_stats:
                continue

            for career_stat in career_stats:
                serializer_class = CAREER_STATS_SERIALIZER_MAP.get(position)
                if not serializer_class:
                    continue 

                career_stat["player"] = player.id
                try:
                    serializer = serializer_class(data=career_stat)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    all_results.append(serializer.data)
                except Exception as e:
                    return Response(
                        {
                            "error": "Career stat validation failed",
                            "error_msg": getattr(e, 'detail', str(e)),
                            "ourlads_position": position,
                            "player_id": player.id,
                            "career_stat": career_stat,
                        },
                        status=400
                    )

            # --- Save Game Stats ---
            game_stats = player_stats.get("game_stats", [])
            for game in game_stats:
                serializer_class = GAME_STATS_SERIALIZER_MAP.get(position)
                if not serializer_class:
                    continue

                game["player"] = player.id
                try:
                    serializer = serializer_class(data=game)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    all_results.append(serializer.data)
                except Exception as e:
                    return Response(
                        {
                            "error": "Game stat validation failed",
                            "error_msg": getattr(e, 'detail', str(e)),
                            "ourlads_position": position,
                            "player_id": player.id,
                            "game": game,
                        },
                        status=400
                    )

        return Response([len(all_results), all_results])

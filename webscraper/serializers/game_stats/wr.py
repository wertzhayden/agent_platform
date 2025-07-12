from webscraper.serializers.game_stats.base import GameStatsBaseSerializer
from webscraper.models.game_stats.wr import ReceiverGameStats

class ReceiverGameStatsSerializer(GameStatsBaseSerializer):
    class Meta(GameStatsBaseSerializer.Meta):
        model = ReceiverGameStats
        fields = GameStatsBaseSerializer.Meta.fields + [
            "receptions", "receiving_yards", "yards_per_catch", "touchdowns", "rush_attempts", 
            "rushing_yards", "avg_per_rush", "rush_touchdowns", "total_fumbles", "lost_fumbles",
        ]
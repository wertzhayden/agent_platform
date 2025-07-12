from webscraper.serializers.game_stats.base import GameStatsBaseSerializer
from webscraper.models.game_stats.rb import RBGameStats

class RBGameStatsSerializer(GameStatsBaseSerializer):
    class Meta(GameStatsBaseSerializer.Meta):
        model = RBGameStats
        fields = GameStatsBaseSerializer.Meta.fields + [
            "attempts", "rushing_yards", "avg_per_rush", "rushing_touchdowns",
            "receptions", "receiving_yards", "yards_per_catch", "receiving_touchdowns",
            "total_fumbles", "lost_fumbles",
        ]

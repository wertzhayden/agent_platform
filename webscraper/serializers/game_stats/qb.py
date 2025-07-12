from webscraper.serializers.game_stats.base import GameStatsBaseSerializer
from webscraper.models.game_stats.qb import QBGameStats

class QBGameStatsSerializer(GameStatsBaseSerializer):
    class Meta(GameStatsBaseSerializer.Meta):
        model = QBGameStats
        fields = GameStatsBaseSerializer.Meta.fields + [
            "completions", "pass_attempts", "completion_percentage", "passing_yards",
            "yards_per_attempt", "passing_touchdowns", "interceptions", "passer_rating",
            "rushing_attempts", "rushing_yards", "avg_per_rush", "rushing_touchdowns",
        ]

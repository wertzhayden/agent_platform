from webscraper.serializers.game_stats.base import GameStatsBaseSerializer
from webscraper.models.game_stats.defense import DefenseGameStats

class DefenseGameStatsSerializer(GameStatsBaseSerializer):
    class Meta(GameStatsBaseSerializer.Meta):
        model = DefenseGameStats
        fields = GameStatsBaseSerializer.Meta.fields + [
            "solo_tackles", "assisted_tackles", "total_tackles", "tackles_for_loss",
            "sacks", "qb_hits", "forced_fumbles", "fumble_recoveries", "interceptions",
            "int_yards", "avg_int_yards", "pass_defended", "touchdowns",
        ]
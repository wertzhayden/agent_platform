from webscraper.serializers.career_stats.base import CareerStatsBaseSerializer
from webscraper.models.career_stats.defense import DefenseCareerStats

class DefenseCareerStatsSerializer(CareerStatsBaseSerializer):
    class Meta(CareerStatsBaseSerializer.Meta):
        model = DefenseCareerStats
        fields = CareerStatsBaseSerializer.Meta.fields + [
            "solo_tackles", "assisted_tackles", "total_tackles", "tackles_for_loss",
            "sacks", "qb_hits", "forced_fumbles", "fumble_recoveries", "interceptions",
            "int_yards", "avg_int_yards", "pass_defended", "touchdowns",
        ]
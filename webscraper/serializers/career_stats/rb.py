from webscraper.serializers.career_stats.base import CareerStatsBaseSerializer
from webscraper.models.career_stats.rb import RBCareerStats

class RBCareerStatsSerializer(CareerStatsBaseSerializer):
    class Meta(CareerStatsBaseSerializer.Meta):
        model = RBCareerStats
        fields = CareerStatsBaseSerializer.Meta.fields + [
            "attempts", "rushing_yards", "avg_per_rush", "rushing_touchdowns",
            "receptions", "receiving_yards", "yards_per_catch", "receiving_touchdowns",
            "total_fumbles", "lost_fumbles",
        ]

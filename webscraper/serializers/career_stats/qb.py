from webscraper.serializers.career_stats.base import CareerStatsBaseSerializer
from webscraper.models.career_stats.qb import QBCareerStats

class QBCareerStatsSerializer(CareerStatsBaseSerializer):
    class Meta(CareerStatsBaseSerializer.Meta):
        model = QBCareerStats
        fields = CareerStatsBaseSerializer.Meta.fields + [
            "completions", "pass_attempts", "completion_percentage", "passing_yards",
            "yards_per_attempt", "passing_touchdowns", "interceptions", "passer_rating",
            "rushing_attempts", "rushing_yards", "avg_per_rush", "rushing_touchdowns",
        ]

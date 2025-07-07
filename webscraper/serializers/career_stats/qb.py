from webscraper.serializers.career_stats.base import CareerStatsBaseSerializer
from webscraper.models.career_stats.qb import QBCareerStats

class QBCareerStatsSerializer(CareerStatsBaseSerializer):
    class Meta(CareerStatsBaseSerializer.Meta):
        model = QBCareerStats
        fields = CareerStatsBaseSerializer.Meta.fields + [
            "completions", "attempts", "completion_percentage", "passing_yards",
            "yards_per_attempt", "passing_touchdowns", "interceptions_thrown",
            "passer_rating", "rush_attempts", "rush_yards", "rush_touchdowns",
            "avg_per_rush", "year",
        ]

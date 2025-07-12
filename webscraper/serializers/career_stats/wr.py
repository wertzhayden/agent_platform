from webscraper.serializers.career_stats.base import CareerStatsBaseSerializer
from webscraper.models.career_stats.wr import ReceiverCareerStats

class ReceiverCareerStatsSerializer(CareerStatsBaseSerializer):
    class Meta(CareerStatsBaseSerializer.Meta):
        model = ReceiverCareerStats
        fields = CareerStatsBaseSerializer.Meta.fields + [
            "receptions", "receiving_yards", "yards_per_catch", "touchdowns", "rush_attempts", 
            "rushing_yards", "avg_per_rush", "rush_touchdowns", "total_fumbles", "lost_fumbles",
    
        ]
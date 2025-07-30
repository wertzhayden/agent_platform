from webscraper.serializers.career_stats.base import CareerStatsBaseSerializer
from webscraper.models.career_stats.wr import ReceiverCareerStats

class ReceiverCareerStatsSerializer(CareerStatsBaseSerializer):
    class Meta(CareerStatsBaseSerializer.Meta):
        model = ReceiverCareerStats
        fields = CareerStatsBaseSerializer.Meta.fields + [
            "receptions", "receiving_yards", "yards_per_catch", "touchdowns", "rush_attempts", 
            "rushing_yards", "avg_per_rush", "rush_touchdowns", "total_fumbles", "lost_fumbles",
    
        ]

    def to_internal_value(self, data):
        # Clean number fields: remove commas and convert to numeric types
        stat_fields = {
        "receptions": int,
        "receiving_yards": int,
        "yards_per_catch": float,
        "touchdowns": int,
        "rush_attempts": int,
        "rushing_yards": int,
        "avg_per_rush": float,
        "rush_touchdowns": int,
        "total_fumbles": int,
        "lost_fumbles": int,
    }

        cleaned_data = data.copy()
        for field, cast_type in stat_fields.items():
            value = cleaned_data.get(field)
            if isinstance(value, str):
                value = value.replace(",", "")
                try:
                    cleaned_data[field] = cast_type(value)
                except ValueError:
                    self.fail(f"{field}: Invalid {cast_type.__name__} value")

        return super().to_internal_value(cleaned_data)
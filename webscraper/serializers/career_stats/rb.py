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
    
    def to_internal_value(self, data):
        # Clean number fields: remove commas and convert to numeric types
        stat_fields = {
        "attempts": int,
        "rushing_yards": int,
        "avg_per_rush": float,
        "rushing_touchdowns": int,
        "receptions": int,
        "receiving_yards": int,
        "yards_per_catch": float,
        "receiving_touchdowns": int,
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


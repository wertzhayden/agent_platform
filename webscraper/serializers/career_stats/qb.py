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

    def to_internal_value(self, data):
        # Clean number fields: remove commas and convert to numeric types
        number_field_casts = {
            "completions": int,
            "pass_attempts": int,
            "passing_yards": int,
            "passing_touchdowns": int,
            "interceptions": int,
            "rushing_attempts": int,
            "rushing_yards": int,
            "rushing_touchdowns": int,
            "completion_percentage": float,
            "yards_per_attempt": float,
            "passer_rating": float,
            "avg_per_rush": float,
        }

        cleaned_data = data.copy()
        for field, cast_type in number_field_casts.items():
            value = cleaned_data.get(field)
            if isinstance(value, str):
                value = value.replace(",", "")
                try:
                    cleaned_data[field] = cast_type(value)
                except ValueError:
                    self.fail(f"{field}: Invalid {cast_type.__name__} value")

        return super().to_internal_value(cleaned_data)

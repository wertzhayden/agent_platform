# core/serializers/player_serializer.py
from rest_framework import serializers
from core.models.player import Player
from webscraper.serializers.school_serializer import SchoolSerializer
from webscraper.serializers.agent_serializer import AgentSerializer

class PlayerSerializer(serializers.ModelSerializer):
    school = SchoolSerializer(read_only=True)
    agent = AgentSerializer(read_only=True)
    jersey_number = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Player
        fields = [
            'id',
            'first_name',
            'last_name',
            'photo_url',
            'high_school',
            'hometown_city',
            'hometown_state',
            'height',
            'weight',
            'jersey_number',
            "side_of_ball",
            'class_year',
            'position',
            'school_link',
            'ourlads_link',
            'school',
            'schools_attended',
            'agent',
            'is_favorited',
            'depth_chart_position',
            'projected_time_to_start',
            'estimated_eligibility_left',
            'thug_position_at_thug_school',
            'hs_class_year',
            'total_stars',
            'star_source',
            'hs_position_rank',
            'overall_hs_rank',
            'experience_level',
            'current_school',
            'age',
            'transfer_rating',
            'transfer_position_rank',
            'transfer_overall_rank',
            'metadata',
        ]

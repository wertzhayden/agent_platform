# core/serializers/player_serializer.py
from rest_framework import serializers
from core.models.player import Player
from core.serializers.school_serializer import SchoolSerializer
from core.serializers.agent_serializer import AgentSerializer
from core.serializers.recruit_serializer import RecruitSerializer

from webscraper.serializers.career_stats.qb import QBCareerStatsSerializer
from webscraper.serializers.career_stats.rb import RBCareerStatsSerializer
from webscraper.serializers.career_stats.wr import ReceiverCareerStatsSerializer
from webscraper.serializers.career_stats.defense import DefenseCareerStatsSerializer


class PlayerSerializer(serializers.ModelSerializer):
    school = SchoolSerializer(read_only=True)
    # agent = AgentSerializer(read_only=True)
    recruits = RecruitSerializer(many=True, read_only=True)  # FK reverse

    # qb_career_stats = QBCareerStatsSerializer(source="qbcareerstats_career_stats", many=True, read_only=True)
    # rb_career_stats = RBCareerStatsSerializer(source="rbcareerstats_career_stats", many=True, read_only=True)
    # receiver_career_stats = ReceiverCareerStatsSerializer(source="receivercareerstats_career_stats", many=True, read_only=True)
    # defense_career_stats = DefenseCareerStatsSerializer(source="defensecareerstats_career_stats", many=True, read_only=True)

    jersey_number = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Player
        fields = '__all__'

# core/serializers/recruit_serializer.py
from rest_framework import serializers
from webscraper.models.recruit import Recruit
from core.serializers.recruiting_class import RecruitingClassSerializer

class RecruitSerializer(serializers.ModelSerializer):
    recruiting_class = RecruitingClassSerializer(read_only=True)

    class Meta:
        model = Recruit
        fields = '__all__'

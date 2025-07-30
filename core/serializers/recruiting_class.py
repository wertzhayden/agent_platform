from rest_framework import serializers
from webscraper.models.recruiting_class import RecruitingClass

class RecruitingClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruitingClass
        fields = [
            "id",
            "school_id",
            "year",
            "overall_rank",
            "transfer_rank",
            "composite_rank",
            "created_at",
            "updated_at",
        ]

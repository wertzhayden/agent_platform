# core/serializers/school_serializer.py
from rest_framework import serializers
from core.models.school import School

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = "__all__" # Add any other relevant fields

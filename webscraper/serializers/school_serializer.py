# core/serializers/school_serializer.py
from rest_framework import serializers
from core.models.school import School

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = ['id', 'name', 'external_name', 'school_id']  # Add any other relevant fields

# core/serializers/agent_serializer.py
from rest_framework import serializers
from core.models.agent import Agent

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ['id', 'name']  # Adjust based on the actual fields

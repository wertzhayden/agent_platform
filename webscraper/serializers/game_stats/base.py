from rest_framework import serializers

class GameStatsBaseSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "player", "year", "metadata"]
        extra_kwargs = {
            "metadata": {"required": False, "allow_null": True}
        }
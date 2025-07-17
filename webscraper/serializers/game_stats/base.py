from rest_framework import serializers

class GameStatsBaseSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "date", "played_against", "player", "metadata"]
        extra_kwargs = {
            "metadata": {"required": False, "allow_null": True}
        }
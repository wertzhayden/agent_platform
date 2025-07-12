from rest_framework import serializers

class CareerStatsBaseSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "player", "season", "metadata"]
        extra_kwargs = {
            "metadata": {"required": False, "allow_null": True}
        }
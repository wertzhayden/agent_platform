from rest_framework import serializers
from core.models.active_nfl_players import ActiveNFLPlayers

class ActiveNFLPlayerSerializer(serializers.ModelSerializer):
    school = serializers.SerializerMethodField()

    class Meta:
        model = ActiveNFLPlayers
        fields = '__all__'
    
    def get_school(self, obj):
        return obj.school.external_name if obj.school else None

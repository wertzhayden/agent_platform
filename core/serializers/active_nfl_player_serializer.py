from rest_framework import serializers
from core.models.active_nfl_players import ActiveNFLPlayers

class ActiveNFLPlayerSerializer(serializers.ModelSerializer):


    class Meta:
        model = ActiveNFLPlayers
        fields = '__all__'

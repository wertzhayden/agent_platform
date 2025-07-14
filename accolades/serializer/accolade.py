from rest_framework import serializers
from accolades.models.accolade import Accolade

class AccoladeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accolade
        fields = "__all__"

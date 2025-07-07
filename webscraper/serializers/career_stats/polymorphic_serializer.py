from rest_polymorphic.serializers import PolymorphicSerializer

from webscraper.models.career_stats.qb import QBCareerStats
from webscraper.models.career_stats.rb import RBCareerStats
from webscraper.models.career_stats.wr import ReceiverCareerStats
from webscraper.models.career_stats.defense import DefenseCareerStats

from webscraper.serializers.career_stats.qb import QBCareerStatsSerializer
from webscraper.serializers.career_stats.rb import RBCareerStatsSerializer
from webscraper.serializers.career_stats.wr import ReceiverCareerStatsSerializer
from webscraper.serializers.career_stats.defense import DefenseCareerStatsSerializer


class CareerStatsPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        QBCareerStats: QBCareerStatsSerializer,
        RBCareerStats: RBCareerStatsSerializer,
        ReceiverCareerStats: ReceiverCareerStatsSerializer,
        DefenseCareerStats: DefenseCareerStatsSerializer,
    }

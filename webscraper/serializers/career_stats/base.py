from rest_polymorphic.serializers import PolymorphicSerializer

class CareerStatsPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        QBCareerStats: QBCareerStatsSerializer,
        RBCareerStats: RBCareerStatsSerializer,
        ReceiverCareerStats: ReceiverCareerStatsSerializer,
        DefenseCareerStats: DefenseCareerStatsSerializer,
    }

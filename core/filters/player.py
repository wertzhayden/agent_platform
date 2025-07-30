import django_filters
from core.models.player import Player

class PlayerFilter(django_filters.FilterSet):
    # Recruit-level filters (through related_name="recruits")
    recruit_stars = django_filters.NumberFilter(field_name="recruits__stars")
    recruit_position = django_filters.CharFilter(field_name="recruits__position", lookup_expr="iexact")
    recruit_status = django_filters.CharFilter(field_name="recruits__status", lookup_expr="iexact")
    recruiting_class_year = django_filters.NumberFilter(field_name="recruits__recruiting_class__year")
    school__conference = django_filters.CharFilter(
        field_name="school__conference", lookup_expr="iexact"
    )

    class Meta:
        model = Player
        fields = ["school__conference", "recruit_stars", "recruit_position", "recruit_status", "recruiting_class_year"]

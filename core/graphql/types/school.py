from graphene_django.types import DjangoObjectType
from core.models.school import School

class SchoolType(DjangoObjectType):
    class Meta:
        model = School
        fields = "__all__"

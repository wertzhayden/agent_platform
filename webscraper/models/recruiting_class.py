from django.db import models
from core.models.base_model import BaseModel
from core.models.school import School

class RecruitingClass(BaseModel):
    """A recruiting class is a collection of players who are recruited in the same year."""
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="recruiting_classes"
    )
    year = models.IntegerField()
    overall_rank = models.IntegerField(blank=True, null=True)
    transfer_rank = models.IntegerField(blank=True, null=True)
    composite_rank = models.IntegerField(blank=True, null=True)
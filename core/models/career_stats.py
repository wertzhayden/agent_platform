from django.db import models
from django.db.models import JSONField
from core.models.base_model import BaseModel
from core.models.player import Player



class CareerStats(BaseModel):
    """One row per player per season."""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="%(class)s_career_stats")
    season = models.IntegerField()
    metadata = JSONField(blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ["-season"]
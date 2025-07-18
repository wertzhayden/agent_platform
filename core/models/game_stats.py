from django.db import models
from django.db.models import JSONField
from core.models.base_model import BaseModel
from core.models.player import Player


class GameStats(BaseModel):
    """One row per player per game."""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="%(class)s_game_stats")
    date = models.CharField(max_length=255, blank=True, null=True)
    played_against = models.CharField(max_length=255, blank=True, null=True)
    metadata = JSONField(blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ["-date"]

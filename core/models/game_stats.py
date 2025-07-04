from django.db import models
from django.contrib.postgres.fields import JSONField
from agent_platform.core.models.base_model import BaseModel
from agent_platform.core.models.player import Player


class GameStats(BaseModel):
    """One row per player per game."""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="game_stats")
    date = models.DateField()
    played_against = models.CharField(max_length=255, blank=True, null=True)
    metadata = JSONField(blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ["-date"]

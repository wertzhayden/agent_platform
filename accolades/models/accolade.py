from django.db import models
from agent_platform.core.models.base_model import BaseModel
from agent_platform.core.models.player import Player

class Accolades(BaseModel):
    """The Awards and Accolades a player has received"""
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="accolades"
    )
    year = models.IntegerField()
    accolade = models.TextField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    conference = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    team = models.IntegerField(blank=True, null=True) # 1st, 2nd, 3rd, 4th, Honorable Mention = 5, etc
    
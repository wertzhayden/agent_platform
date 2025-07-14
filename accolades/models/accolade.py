from django.db import models
from core.models.base_model import BaseModel
from core.models.player import Player

class Accolade(BaseModel):
    """The Awards and Accolades a player has received"""
    player = models.ForeignKey(
        Player, 
        on_delete=models.CASCADE, 
        related_name="accolades",
        blank=True,
        null=True
    )
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    year = models.IntegerField()
    # Award = Freshman All-American, Team = 1st/2nd/etc..., source = 247sports, conference = None 
    name_of_award = models.TextField(blank=True, null=True)
    team = models.IntegerField(blank=True, null=True) # 1st, 2nd, 3rd, 4th, Honorable Mention = 5, etc
    source = models.TextField(blank=True, null=True)
    conference = models.TextField(blank=True, null=True)
    
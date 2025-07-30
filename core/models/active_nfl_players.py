from django.db import models
from django.contrib.postgres.fields import ArrayField

from core.models.base_model import BaseModel
from core.models.agent import Agent
from core.models.school import School


class ActiveNFLPlayers(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="active_nfl_players")
    team = models.TextField(blank=True, null=True, help_text="NFL team the player is currently on")
    name = models.TextField(blank=True, null=True, help_text="Name of the active NFL player")
    position = models.TextField(blank=True, null=True, help_text="Position of the active NFL player")
    ourlads_position = models.CharField(max_length=50, blank=True, null=True, help_text="Ourlads Position on NFL Depth Charts")
    depth_chart_position = models.IntegerField(
        help_text="1=starter, 2=backup, etc", blank=True, null=True
    )
    roster_status = models.CharField(
        max_length=50, null=True, blank=True, help_text="Roster Status (e.g. Active, RES, etc...)"
    )
    draft_year = models.IntegerField(blank=True, null=True, help_text="Draft Year of the player")
    draft_round = models.IntegerField(blank=True, null=True, help_text="Draft Round of the player")
    overall_draft_pick = models.IntegerField(blank=True, null=True, help_text="Draft Pick of the player")
    
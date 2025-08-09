from django.db import models
from django.contrib.postgres.fields import ArrayField

from core.models.base_model import BaseModel
from core.models.agent import Agent
from core.models.school import School


class ActiveNFLPlayers(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="active_nfl_players")
    first_name = models.TextField(blank=True, null=True, help_text="First name of the active NFL player")
    last_name = models.TextField(blank=True, null=True, help_text="Last name of the active NFL player")
    team = models.TextField(blank=True, null=True, help_text="NFL team the player is currently on")
    position = models.TextField(blank=True, null=True, help_text="Position of the active NFL player")
    ourlads_position = models.CharField(max_length=50, blank=True, null=True, help_text="Ourlads Position on NFL Depth Charts")
    ourlads_second_position = models.CharField(max_length=50, blank=True, null=True, help_text="Ourlads Second Position on NFL Depth Charts. Typically for Special Teams with Kickers / Holders")
    depth_chart_position = models.IntegerField(
        help_text="1=starter, 2=backup, etc", blank=True, null=True
    )
    depth_chart_second_position = models.IntegerField(
        help_text="1=starter, 2=backup, etc for Special Teams", blank=True, null=True
    )
    roster_status = models.CharField(
        max_length=50, null=True, blank=True, help_text="Roster Status (e.g. Active, RES, etc...)"
    )
    ourlads_link = models.TextField(blank=True, null=True, help_text="Ourlads Link to the player profile")
    draft_year = models.IntegerField(blank=True, null=True, help_text="Draft Year of the player")
    draft_round = models.IntegerField(blank=True, null=True, help_text="Draft Round of the player")
    overall_draft_pick = models.CharField(max_length=24, blank=True, null=True, help_text="Draft Pick of the player")
    years_of_experience = models.IntegerField(blank=True, null=True, help_text="Years of Experience in the NFL")
    age = models.FloatField(blank=True, null=True, help_text="Age of the player in years")
    agents = ArrayField(models.TextField(), blank=True, null=True, help_text="List of Agents representing the player")
    spot_trac_id = models.IntegerField(blank=True, null=True, help_text="Spotrac ID for the player")
    firm = models.TextField(blank=True, null=True, help_text="Agent Firm representing the player")
    current_cap_hit = models.FloatField(blank=True, null=True, help_text="Current Cap Hit for the player")
    current_year_cash_salary = models.FloatField(blank=True, null=True, help_text="Current Year Cash Salary for the player")
    career_earnings = models.FloatField(blank=True, null=True, help_text="Career Earnings of the player")

    class Meta:
        unique_together = (
            ("school", "first_name", "last_name"),
        )

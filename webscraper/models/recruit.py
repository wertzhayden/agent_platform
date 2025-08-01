from django.db import models
from core.models.base_model import BaseModel
from core.models.player import Player
from webscraper.models.recruiting_class import RecruitingClass

class Recruit(BaseModel):
    """A recruit is a player from a schools' recruiting class in a given year"""
    recruiting_class = models.ForeignKey(
        RecruitingClass, on_delete=models.CASCADE, related_name="recruiting_classes"
    )
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    high_school = models.CharField(max_length=255, blank=True, null=True)
    hometown_city = models.CharField(max_length=100, blank=True, null=True)
    hometown_state = models.CharField(max_length=100, blank=True, null=True)
    height = models.CharField(max_length=10, blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    stars = models.IntegerField(blank=True, null=True)
    hs_rating_score = models.IntegerField(blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    national_rank = models.IntegerField(blank=True, null=True)
    position_rank = models.IntegerField(blank=True, null=True)
    state_rank = models.IntegerField(blank=True, null=True)
    transfer_national_rank = models.IntegerField(blank=True, null=True)
    transfer_position_rank = models.IntegerField(blank=True, null=True)
    transfer_state_rank = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    school_link = models.URLField(blank=True, null=True)
    transfer_stars = models.IntegerField(blank=True, null=True)
    transfer_rating_score = models.FloatField(blank=True, null=True)
    current_position = models.CharField(max_length=50, blank=True, null=True)
    current_height = models.CharField(max_length=50, blank=True, null=True)
    current_weight = models.IntegerField(blank=True, null=True)
    experience_level_at_current_school = models.CharField(max_length=100, blank=True, null=True)
    current_school = models.CharField(max_length=255, blank=True, null=True)
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name="recruits")
    jersey_number = models.IntegerField(blank=True, null=True)
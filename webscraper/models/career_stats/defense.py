from django.db import models
from core.models.career_stats import CareerStats

class DefenseCareerStats(CareerStats):
    solo_tackles = models.IntegerField()
    assisted_tackles = models.IntegerField()
    total_tackles = models.FloatField()
    tackles_for_loss = models.FloatField()
    sacks = models.FloatField()
    qb_hits = models.IntegerField()
    forced_fumbles = models.IntegerField()
    fumble_recoveries = models.IntegerField()
    interceptions = models.IntegerField()
    int_yards = models.IntegerField()
    avg_int_yards = models.FloatField()
    touchdowns = models.IntegerField()
    pass_defended = models.IntegerField(help_text="Includes pass breakups & INTs")

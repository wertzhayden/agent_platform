from django.db import models
from core.models.career_stats import CareerStats

class RBCareerStats(CareerStats):
    attempts = models.IntegerField()
    rushing_yards = models.IntegerField()
    avg_per_rush = models.FloatField()
    rushing_touchdowns = models.IntegerField()
    receptions = models.IntegerField()
    receiving_yards = models.IntegerField()
    yards_per_catch = models.FloatField()
    receiving_touchdowns = models.IntegerField()
    total_fumbles = models.IntegerField()
    lost_fumbles = models.IntegerField()
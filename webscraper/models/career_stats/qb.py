from django.db import models
from core.models.career_stats import CareerStats

class QBCareerStats(CareerStats):
    completions = models.IntegerField()
    attempts = models.IntegerField()
    completion_percentage = models.FloatField()
    passing_yards = models.IntegerField()
    yards_per_attempt = models.FloatField()
    passing_touchdowns = models.IntegerField()
    interceptions_thrown  = models.IntegerField()
    passer_rating = models.FloatField()
    rush_attempts = models.IntegerField()
    rush_yards = models.IntegerField()
    avg_per_rush = models.FloatField()
    rush_touchdowns = models.IntegerField()
from django.db import models
from core.models.game_stats import GameStats


class QBGameStats(GameStats):
    completions = models.IntegerField()
    pass_attempts = models.IntegerField()
    completion_percentage = models.FloatField()
    passing_yards = models.IntegerField()
    yards_per_attempt = models.FloatField()
    passing_touchdowns = models.IntegerField()
    interceptions = models.IntegerField()
    passer_rating = models.FloatField()
    rushing_attempts = models.IntegerField()
    rushing_yards = models.IntegerField()
    avg_per_rush = models.FloatField()
    rushing_touchdowns = models.IntegerField()
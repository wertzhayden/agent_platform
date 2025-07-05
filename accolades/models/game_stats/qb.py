from django.db import models
from core.models.game_stats import GameStats


class QBGameStats(GameStats):
    completions = models.IntegerField()
    attempts = models.IntegerField()
    completion_percentage = models.FloatField()
    passing_yards = models.IntegerField()
    yards_per_attempt = models.FloatField()
    passing_touchdowns = models.IntegerField()
    interceptions_thrown = models.IntegerField()
    passer_rating = models.FloatField()
    rush_attempts = models.IntegerField()
    rush_yards = models.IntegerField()
    rush_touchdowns = models.IntegerField()
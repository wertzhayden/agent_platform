from django.db import models
from agent_platform.core.models.game_stats import GameStats

class ReceiverGameStats(GameStats):
    receptions = models.IntegerField()
    receiving_yards = models.IntegerField()
    yards_per_catch = models.FloatField()
    touchdowns = models.IntegerField()
    rush_attempts = models.IntegerField()
    rushing_yards = models.IntegerField()
    avg_per_rush = models.FloatField()
    total_fumbles = models.IntegerField()
    lost_fumbles = models.IntegerField()
from django.db import models
from django.contrib.postgres.fields import JSONField  # or use models.JSONField on Django ≥3.1
from models.generic_models import BaseModel

# -- Abstract base classes --

class CareerStats(BaseModel):
    """One row per player per season."""
    player = models.ForeignKey(
        "yourapp.Player", on_delete=models.CASCADE, related_name="%(class)s_career"
    )
    year = models.IntegerField()
    metadata = JSONField(blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ["-year"]


class GameStats(BaseModel):
    """One row per player per game."""
    player = models.ForeignKey(
        "yourapp.Player", on_delete=models.CASCADE, related_name="%(class)s_game"
    )
    date = models.DateField()
    played_against = models.CharField(max_length=255, blank=True, null=True)
    metadata = JSONField(blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ["-date"]


# -- QB stats --

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
    rush_touchdowns = models.IntegerField()


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


# -- Receiver stats --

class ReceiverCareerStats(CareerStats):
    receptions = models.IntegerField()
    receiving_yards = models.IntegerField()
    yards_per_catch = models.FloatField()
    touchdowns = models.IntegerField()
    rush_attempts = models.IntegerField()
    rushing_yards = models.IntegerField()
    avg_per_rush = models.FloatField()
    total_fumbles = models.IntegerField()
    lost_fumbles = models.IntegerField()


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


# -- Running Back stats --

class RBCareerStats(CareerStats):
    rush_attempts = models.IntegerField()
    rushing_yards = models.IntegerField()
    avg_per_rush = models.FloatField()
    receptions = models.IntegerField()
    receiving_yards = models.IntegerField()
    yards_per_catch = models.FloatField()
    receiving_touchdowns = models.IntegerField()
    total_fumbles = models.IntegerField()
    lost_fumbles = models.IntegerField()


class RBGameStats(GameStats):
    rush_attempts = models.IntegerField()
    rushing_yards = models.IntegerField()
    avg_per_rush = models.FloatField()
    receptions = models.IntegerField()
    receiving_yards = models.IntegerField()
    yards_per_catch = models.FloatField()
    receiving_touchdowns = models.IntegerField()
    total_fumbles = models.IntegerField()
    lost_fumbles = models.IntegerField()


# -- Defense stats --

class DefenseCareerStats(CareerStats):
    solo_tackles = models.IntegerField()
    assisted_tackles = models.IntegerField()
    total_tackles_for_loss = models.FloatField()
    sacks = models.FloatField()
    qb_hits = models.IntegerField()
    forced_fumbles = models.IntegerField()
    fumble_recoveries = models.IntegerField()
    interceptions = models.IntegerField()
    int_yards = models.IntegerField()
    avg_int_yards = models.FloatField()
    pass_defended = models.IntegerField(help_text="Includes pass breakups & INTs")


class DefenseGameStats(GameStats):
    solo_tackles = models.IntegerField()
    assisted_tackles = models.IntegerField()
    total_tackles_for_loss  = models.FloatField()
    sacks = models.FloatField()
    qb_hits = models.IntegerField()
    forced_fumbles = models.IntegerField()
    fumble_recoveries = models.IntegerField()
    interceptions = models.IntegerField()
    int_yards = models.IntegerField()
    avg_int_yards = models.FloatField()
    pass_defended = models.IntegerField(help_text="Includes pass breakups & INTs")


# -- Transfer Rankings --

class TransferRanking(models.Model):
    player_id = models.ForeignKey("agent_platform.Player",on_delete=models.CASCADE, related_name="transfer_rankings")
    player_transfer_rank = models.IntegerField()
    nil_value = models.IntegerField(blank=True, null=True)
    school_from = models.ForeignKey("agent_platform.School", on_delete=models.PROTECT, related_name="transfers_out")
    school_to = models.ForeignKey("agent_platform.School", on_delete=models.PROTECT, related_name="transfers_in")
    year = models.IntegerField()
    metadata = JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-year"]
        unique_together = ("player", "year", "school_from", "school_to")

    def __str__(self):
        return (
            f"{self.player} → {self.school_to} "
            f"({self.year}) rank #{self.player_transfer_rank}"
        )

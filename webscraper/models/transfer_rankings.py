from django.db import models
from django.contrib.postgres.fields import JSONField

from agent_platform.core.models.player import Player

class TransferRanking(models.Model):
    player_id = models.ForeignKey(Player,on_delete=models.CASCADE, related_name="transfer_rankings")
    player_transfer_rank = models.IntegerField()
    nil_value = models.IntegerField(blank=True, null=True)
    # School ID 
    school_from = models.TextField(blank=True, null=True)
    # School ID
    school_to = models.TextField(blank=True, null=True)
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

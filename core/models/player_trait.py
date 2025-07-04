from django.db import models
from agent_platform.core.models.base_model import BaseModel
from agent_platform.core.models.player import Player
from agent_platform.core.models.trait import Trait

class PlayerTrait(BaseModel):
    """
    The join‐table.  For each (player, trait) pair:
      • which option they picked
      • the total_score (pillar_score * multiplier * some factor?)
    """
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    trait  = models.ForeignKey(Trait, on_delete=models.CASCADE)

    # the value they actually picked:
    selected_option = models.CharField(max_length=100)

    # computed when saving (or you could make it a @property if you prefer)
    total_score = models.FloatField(editable=False)

    class Meta:
        unique_together = ("player", "trait")
        indexes = [
            models.Index(fields=["trait", "total_score"]),
        ]

    def save(self, *args, **kwargs):
        # recalc total_score each time
        # here we assume pillar_score * multiplier,
        # but you can incorporate the selected_option if it carries weight.
        self.total_score = (self.trait.score + self.trait.pillar_score) * self.trait.multipler if self.trait else 0.0

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.player} — {self.trait.name}: "
            f"{self.selected_option} ({self.total_score})"
        )
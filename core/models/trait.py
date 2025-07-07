from django.db import models
from django.contrib.postgres.fields import ArrayField
from core.models.base_model import BaseModel


class Trait(BaseModel):
    """
    The master list of traits—each one knows its own dropdown options
    and its weighting formula.
    """
    name = models.CharField(max_length=100, unique=True)
    dropdown_options = ArrayField(
        base_field=models.CharField(max_length=100),
        help_text="The list of choices a player can pick for this trait",
    )
    score = models.FloatField()
    pillar_score = models.FloatField()
    multiplier   = models.FloatField()

    def __str__(self):
        return self.name

    # @property
    # def max_score(self) -> float:
    #     # if every option is “worth” the same, you could do:
    #     if self.score and self.pillar_score and self.multiplier:
    #         return (self.score + self.pillar_score) * self.multiplier
    #     return 0.0
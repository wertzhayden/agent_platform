from django.db import models
from django.contrib.postgres.fields import ArrayField

from core.models.base_model import BaseModel
from core.models.agent import Agent


class School(BaseModel):
    name = models.CharField(max_length=255)
    # External name is used to match the school with external data sources (e.g. Ourlads & 247Sports)
    external_name = models.CharField(max_length=255, blank=True, null=True)
    # The unique identifier for the school, used to match with external data sources (e.g. Ourlads)
    school_id = models.CharField(max_length=100, unique=True)
    # Created so that we can filter schools by their associated agents
    key_agents = models.ManyToManyField(Agent, blank=True,)
    # Thug Positions by School
    thug_positions = ArrayField(
        base_field=models.CharField(max_length=128),
        default=list,
        blank=True,
        help_text="A list of thug positions that the school is known for"
    )
    metadata = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name

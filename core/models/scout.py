from django.db import models
from django.contrib.postgres.fields import ArrayField
from core.models.base_model import BaseModel
from core.models.user import User
from core.models.agent import Agent

class Scout(BaseModel):
    """Agent sends Players to the Scout for review, eval and next steps in their workflow"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scouts')
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name="scouts",
        help_text="The agent this scout works for"
    )
    favorite_players = ArrayField(
        base_field=models.TextField(),
        default=list,
        blank=True,
        help_text="A list of players that the Agent has identified as favorites or potential clients"
    )
    metadata = models.JSONField(blank=True, null=True)
from django.db import models
from django.contrib.postgres.fields import ArrayField
from core.models.base_model import BaseModel
from core.models.user import User
from core.models.firm import Firm
# from core.models.player import Player


class Agent(BaseModel):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agents')
    firm = models.ForeignKey(
        Firm,
        on_delete=models.CASCADE,
        related_name="agents",
        help_text="The firm that the agent works for"
    )
    key_schools = ArrayField(
        base_field=models.TextField(),
        default=list,
        blank=True,
        help_text="A list schools that the agent is formally associated with"
    )
    favorite_players = ArrayField(
        base_field=models.TextField(),
        default=list,
        blank=True,
        help_text="A list of players that the Agent has identified as favorites or potential clients"
    )
    shared_players = ArrayField(
        base_field=models.TextField(),
        default=list,
        blank=True,
        help_text="A list of players that the Agent has shared with other agents or firms"
    )
    # player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name="agent-players")
    metadata = models.JSONField(blank=True, null=True)
from django.db import models
from django.contrib.postgres.fields import ArrayField

from agent_platform.core.models.base_model import BaseModel
from agent_platform.core.models.trait import Trait
from agent_platform.core.models.school import School
from agent_platform.core.models.agent import Agent



class Player(BaseModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    photo_url = models.URLField(blank=True, null=True)
    high_school = models.CharField(max_length=255, blank=True, null=True)
    hometown_city = models.CharField(max_length=100, blank=True, null=True)
    hometown_state = models.CharField(max_length=100, blank=True, null=True)
    height = models.CharField(max_length=10,blank=True, null=True)
    weight = models.IntegerField(blank=True, null=True)
    jersey_number = models.IntegerField(blank=True, null=True)
    class_year = models.CharField(max_length=50, blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    # 247 Sports Link
    player_school_link = models.URLField(blank=True, null=True)
    # Ourlads Link
    player_ourlads_link = models.URLField(blank=True, null=True)
    # hook up to TraitDefinition via the through table below
    traits = models.ManyToManyField(
        Trait,
        through="PlayerTrait",
        related_name="players",
        blank=True,
    )
    school = models.ForeignKey(
        School, on_delete=models.PROTECT, related_name="players"
    )
    schools_attended = ArrayField(
        base_field=models.TextField(),
        default=list,
        blank=True,
        help_text="A list of schools that the player has attended"
    )
    agent = models.ForeignKey(
        Agent, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_favorited = models.BooleanField(default=False)
    depth_chart_position = models.IntegerField(
        help_text="1=starter, 2=backup, etc", blank=True, null=True
    )
    projected_time_to_start = models.IntegerField(
        help_text="years until expected to start, or 0=now", blank=True, null=True
    )
    estimated_eligibility_left = models.IntegerField(
        help_text="0–3 years", blank=True, null=True
    )

    thug_position_at_thug_school = models.BooleanField(default=False)
    hs_class_year = models.IntegerField(blank=True, null=True)
    total_stars = models.IntegerField(blank=True, null=True)
    # now an ArrayField of star-source strings
    star_source = ArrayField(
        base_field=models.CharField(max_length=50),
        default=list,
        blank=True,
        help_text="e.g. ['247sports','on3']"
    )
    hs_position_rank = models.IntegerField(blank=True, null=True)
    overall_hs_rank = models.IntegerField(blank=True, null=True)
    experience_level = models.CharField(max_length=100, blank=True, null=True)
    current_school = models.CharField(max_length=255, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)

    transfer_rating = models.IntegerField(blank=True, null=True)
    transfer_position_rank = models.IntegerField(blank=True, null=True)
    transfer_overall_rank = models.IntegerField(blank=True, null=True)

    metadata = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
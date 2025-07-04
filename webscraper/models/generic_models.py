from django.db import models
from django.contrib.postgres.fields import ArrayField

class BaseModel(models.Model):
    """Base model to provide common fields for all models in the application."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# Create your models here.
class User(BaseModel):
    """User model to store user information"""
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed passwords

    def __str__(self):
        return self.username
    

class Firm(BaseModel):
    """Firm model to represent the Firm at which the agents work"""
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    num_of_employees = models.IntegerField() # Number of employees
    metadata = models.JSONField(blank=True, null=True)

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
    metadata = models.JSONField(blank=True, null=True)


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


class School(BaseModel):
    name = models.CharField(max_length=255)
    # External name is used to match the school with external data sources (e.g. Ourlads & 247Sports)
    external_name = models.CharField(max_length=255, blank=True, null=True)
    # The unique identifier for the school, used to match with external data sources (e.g. Ourlads)
    school_id = models.CharField(max_length=100, unique=True)
    # Created so that we can filter schools by their associated agents
    key_agents = models.ManyToManyField(Agent, blank=True)
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
    
class TraitDefinition(models.Model):
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

    @property
    def max_score(self) -> float:
        # if every option is “worth” the same, you could do:
        if self.score and self.pillar_score and self.multiplier:
            return (self.score + self.pillar_score) * self.multiplier
        return 0.0

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
        TraitDefinition,
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

class PlayerTrait(models.Model):
    """
    The join‐table.  For each (player, trait) pair:
      • which option they picked
      • the total_score (pillar_score * multiplier * some factor?)
    """
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    trait  = models.ForeignKey(TraitDefinition, on_delete=models.CASCADE)

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
    

class RecruitingClass(BaseModel):
    """A recruiting class is a collection of players who are recruited in the same year."""
    school_id = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="recruiting_classes"
    )
    year = models.IntegerField()
    overall_rank = models.IntegerField(blank=True, null=True)
    transfer_rank = models.IntegerField(blank=True, null=True)
    composite_rank = models.IntegerField(blank=True, null=True)

class Accolades(BaseModel):
    """The Awards and Accolades a player has received"""
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="accolades"
    )
    year = models.IntegerField()
    accolade = models.TextField(blank=True, null=True)
    source = models.TextField(blank=True, null=True)
    conference = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    team = models.IntegerField(blank=True, null=True) # 1st, 2nd, 3rd, 4th, Honorable Mention = 5, etc
    
from django.db import models
from agent_platform.core.models.base_model import BaseModel

class Firm(BaseModel):
    """Firm model to represent the Firm at which the agents work"""
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    num_of_employees = models.IntegerField() # Number of employees
    metadata = models.JSONField(blank=True, null=True)
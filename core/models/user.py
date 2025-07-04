from django.db import models
from agent_platform.core.models.base_model import BaseModel

class User(BaseModel):
    """User model to store user information"""
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed passwords

    def __str__(self):
        return self.username
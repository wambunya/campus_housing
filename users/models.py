from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_landlord = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True)
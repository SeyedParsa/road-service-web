from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class State(models.TextChoices):
        SIMPLE = 'SP'
        CITIZEN = 'CZ'
        SERVICEMAN = 'SM'
        COUNTRY_MODERATOR = 'PR'
        PROVINCE_MODERATOR = 'PM'
        COUNTY_MODERATOR = 'CM'
        COUNTY_EXPERT = 'CE'

    name = models.CharField(max_length=50, verbose_name="Display Name")
    phone_number = models.CharField(max_length=12)
    state = models.CharField(max_length=2, choices=State.choices, default=State.SIMPLE)

    def __str__(self):
        return self.username

    def has_role(self):
        return self.state != self.State.SIMPLE

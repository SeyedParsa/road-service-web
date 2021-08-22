from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    name = models.CharField(max_length=50, verbose_name="Display Name")
    phone_number = models.CharField(max_length=12, unique=True)

    def __str__(self):
        return self.username

    def has_role(self):
        return hasattr(self, 'role')


class Role(models.Model):
    class Type(models.TextChoices):
        CITIZEN = 'CZ'
        SERVICEMAN = 'SM'
        COUNTRY_MODERATOR = 'PR'
        PROVINCE_MODERATOR = 'PM'
        COUNTY_MODERATOR = 'CM'
        COUNTY_EXPERT = 'CE'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=Type.choices)

    def __str__(self):
        return '%s %s' % (self.user, self.type)

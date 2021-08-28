from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    name = models.CharField(max_length=50, verbose_name="Display Name")
    phone_number = models.CharField(max_length=12, unique=True)

    def __str__(self):
        return self.username

    def has_role(self):
        return hasattr(self, 'role')

    def login(self):
        pass

    def request_password_recovery(self):
        pass

    def request_phone_authentication(self):
        pass

    def change_password(self, old_password, new_password):
        if self.password == old_password:
            self.password = new_password
            self.save()
            self.refresh_from_db()
            return True
        raise Exception ('Login info authentication failed')


class Role(models.Model):
    class Type(models.TextChoices):
        CITIZEN = 'CZ'
        SERVICEMAN = 'SM'
        COUNTRY_MODERATOR = 'PR'
        PROVINCE_MODERATOR = 'PM'
        COUNTY_MODERATOR = 'CM'
        COUNTY_EXPERT = 'CE'

    user = models.OneToOneField(User, related_name='role', on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=Type.choices)

    def get_concrete(self):
        if self.type == Role.Type.CITIZEN:
            return self.citizen
        elif self.type == Role.Type.SERVICEMAN:
            return self.serviceman
        elif self.type == Role.Type.COUNTRY_MODERATOR:
            return self.moderator.countrymoderator
        elif self.type == Role.Type.PROVINCE_MODERATOR:
            return self.moderator.provincemoderator
        elif self.type == Role.Type.COUNTY_MODERATOR:
            return self.moderator.countymoderator
        elif self.type == Role.Type.countyexpert:
            return self.countyexpert

    def __str__(self):
        return '%s %s' % (self.type, self.user)

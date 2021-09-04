from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.exceptions import WeakPasswordError
from sms.models import SmsSender


class User(AbstractUser):
    name = models.CharField(max_length=50, verbose_name="Display Name")
    phone_number = models.CharField(max_length=12, unique=True)

    def __str__(self):
        return self.username

    def has_role(self):
        return hasattr(self, 'role')

    def change_password(self, password):
        try:
            validate_password(password)
            self.set_password(password)
            self.save()
        except ValidationError:
            raise WeakPasswordError()

    def send_reset_password_link(self):
        uid = urlsafe_base64_encode(force_bytes(self.pk))
        token = default_token_generator.make_token(self)
        link = 'http://%s/reset/%s/%s/' % (settings.DOMAIN, uid, token)
        message = 'امدادرسانان جاده\n\nلینک بازیابی رمز عبور: %s' % link
        SmsSender.get_instance().send_to_number(self.phone_number, message)


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

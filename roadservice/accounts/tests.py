from django.test import TestCase

from accounts.exceptions import WeakPasswordError
from accounts.models import User


class UserTestCase(TestCase):
    def test_change_password(self):
        user = User.objects.create(name='parsa', phone_number='1234')
        with self.assertRaises(WeakPasswordError):
            user.change_password('parsa')
        with self.assertRaises(WeakPasswordError):
            user.change_password('mypassword')
        with self.assertRaises(WeakPasswordError):
            user.change_password('1234')
        password = 'hello1234#!?'
        user.change_password(password)
        self.assertTrue(user.check_password(password))

    def test_send_reset_password_link(self):
        pass  # test manually

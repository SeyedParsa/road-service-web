from django.utils import timezone
from django.test import TestCase


class BaseTestCase(TestCase):
    def setUp(self):
        pass

    def test_sample(self):
        print(timezone.now())

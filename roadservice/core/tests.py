from django.test import TestCase
from accounts.models import User
from core.models import Country, Province, County, CountryModerator, ProvinceModerator


class ModeratorsTestCase(TestCase):
    def setUp(self):
        self.parsa = User.objects.create(username='parsa')
        self.kiarash = User.objects.create(username='kiarash')
        self.majid = User.objects.create(username='majid')
        self.mahdi = User.objects.create(username='mahdi')
        self.iran = Country.objects.create(name='Iran')
        self.tehran = Province.objects.create(name='Tehran', country=self.iran)
        self.shiraz = Province.objects.create(name='Tehran', country=self.iran)
        self.damavand = County.objects.create(name='Damavand', province=self.tehran)
        self.firoozkooh = County.objects.create(name='Firoozkooh', province=self.tehran)
        self.president = CountryModerator.objects.create(user=self.parsa, country=self.iran)
        self.assertEqual(self.iran.countrymoderator.user, self.parsa)

    def test_moderator_assignment(self):
        tehran_moderator = self.president.assign_province_moderator(self.kiarash, self.tehran)
        self.assertEqual(self.tehran.provincemoderator.user, self.kiarash)
        tehran_moderator.assign_county_moderator(self.majid, self.damavand)
        self.assertEqual(self.damavand.countymoderator.user, self.majid)
        with self.assertRaisesMessage(Exception, 'The user is already the moderator of the province'):
            self.president.assign_province_moderator(self.kiarash, self.tehran)
        with self.assertRaisesMessage(Exception, 'The user is already the moderator of the county'):
            tehran_moderator.assign_county_moderator(self.majid, self.damavand)
        with self.assertRaisesMessage(Exception, 'The user has a role'):
            self.president.assign_province_moderator(self.majid, self.shiraz)
        with self.assertRaisesMessage(Exception, 'The user has a role'):
            tehran_moderator.assign_county_moderator(self.kiarash, self.firoozkooh)
        self.president.assign_province_moderator(self.mahdi, self.tehran)
        self.president.assign_province_moderator(self.kiarash, self.shiraz)
        self.assertEqual(self.tehran.provincemoderator.user, self.mahdi)
        self.assertEqual(self.shiraz.provincemoderator.user, self.kiarash)


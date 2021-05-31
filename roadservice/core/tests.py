from django.test import TestCase
from accounts.models import User
from core.models import Country, Province, County, CountryModerator, ProvinceModerator, Citizen, Serviceman, \
    ServiceTeam, Speciality, CountyExpert, Issue, MachineryType, Machinery, MissionType


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


class AppectIssueTestCase(TestCase):
    def setUp(self):
        iran = Country.objects.create(name='Iran')
        tehran = Province.objects.create(name='Tehran', country=iran)
        shemiran = County.objects.create(name='Shemiran', province=tehran)
        worker_user = User.objects.create(username='worker')
        reporter_user = User.objects.create(username='reporter')
        expert_user = User.objects.create(username='expert')
        self.asphalt_fixing = Speciality.objects.create(name='Fixing Asphalt')
        self.team = ServiceTeam.objects.create(county=shemiran, speciality=self.asphalt_fixing)
        worker = Serviceman.objects.create(user=worker_user, team=self.team, lat=1, long=1)
        reporter = Citizen.objects.create(user=reporter_user)
        self.expert = CountyExpert.objects.create(user=expert_user, county=shemiran)
        self.issue = Issue.objects.create(title='Asphalt needs fixing',
                                          description='.',
                                          reporter=reporter,
                                          county=shemiran)
        self.crane_type = MachineryType.objects.create(name='Crane')
        self.crane = Machinery.objects.create(type=self.crane_type, county=shemiran, total_count=10, available_count=10)
        self.service_type = MissionType.objects.create(name='Service')

    def test_assignment_fail(self):
        self.expert.accept_issue(self.issue, self.service_type, [(self.asphalt_fixing, 2)], [(self.crane_type, 15)])
        self.assertEqual(self.issue.state, Issue.State.FAILED)

    def test_assignment_successful(self):
        self.expert.accept_issue(self.issue, self.service_type, [(self.asphalt_fixing, 1)], [(self.crane_type, 3)])
        self.issue.refresh_from_db()
        self.team.refresh_from_db()
        self.crane.refresh_from_db()
        self.assertEqual(self.issue.state, Issue.State.ASSIGNED)
        self.assertEqual(self.team.active_mission, self.issue.mission)
        self.assertEqual(self.crane.available_count, 7)

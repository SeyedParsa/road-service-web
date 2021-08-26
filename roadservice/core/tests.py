from django.test import TestCase
from accounts.models import User
from core.models import Country, Province, County, CountryModerator, ProvinceModerator, Citizen, Serviceman, \
    ServiceTeam, Speciality, CountyExpert, Issue, MachineryType, Machinery, MissionType


class ModeratorsTestCase(TestCase):
    def setUp(self):
        self.parsa = User.objects.create(username='parsa', phone_number='0')
        self.kiarash = User.objects.create(username='kiarash', phone_number='1')
        self.majid = User.objects.create(username='majid', phone_number='2')
        self.mahdi = User.objects.create(username='mahdi', phone_number='3')
        self.iran = Country.objects.create(name='Iran')
        self.tehran = Province.objects.create(name='Tehran', super_region=self.iran)
        self.tehran.refresh_from_db()
        self.shiraz = Province.objects.create(name='Shiraz', super_region=self.iran)
        self.shiraz.refresh_from_db()
        self.damavand = County.objects.create(name='Damavand', super_region=self.tehran)
        self.damavand.refresh_from_db()
        self.firoozkooh = County.objects.create(name='Firoozkooh', super_region=self.tehran)
        self.firoozkooh.refresh_from_db()
        self.president = CountryModerator.objects.create(user=self.parsa, region=self.iran)
        self.iran.refresh_from_db()

    def test_moderator_assignment(self):
        self.assertEqual(self.iran.moderator.user, self.parsa)
        tehran_moderator = self.president.assign_moderator(self.kiarash, self.tehran.region_ptr)
        self.assertEqual(self.tehran.moderator.user, self.kiarash)
        tehran_moderator.assign_moderator(self.majid, self.damavand.region_ptr)
        self.assertEqual(self.damavand.moderator.user, self.majid)
        with self.assertRaisesMessage(Exception, 'The region is not in the moderator\'s subregions'):
            tehran_moderator.assign_moderator(self.mahdi, self.shiraz.region_ptr)
        with self.assertRaisesMessage(Exception, 'The user is already the moderator of the region'):
            self.president.assign_moderator(self.kiarash, self.tehran.region_ptr)
        with self.assertRaisesMessage(Exception, 'The user has a role'):
            self.president.assign_moderator(self.majid, self.shiraz.region_ptr)

        self.president.assign_moderator(self.mahdi, self.tehran.region_ptr)
        self.kiarash.refresh_from_db()
        self.tehran.refresh_from_db()
        self.president.assign_moderator(self.kiarash, self.shiraz.region_ptr)
        self.assertEqual(self.tehran.moderator.user, self.mahdi)
        self.assertEqual(self.shiraz.moderator.user, self.kiarash)


class AcceptIssueTestCase(TestCase):
    def setUp(self):
        iran = Country.objects.create(name='Iran')
        tehran = Province.objects.create(name='Tehran', super_region=iran)
        shemiran = County.objects.create(name='Shemiran', super_region=tehran)
        serviceman_user = User.objects.create(username='serviceman', phone_number='0')
        reporter_user = User.objects.create(username='reporter', phone_number='1')
        expert_user = User.objects.create(username='expert', phone_number='2')
        self.asphalt_fixing = Speciality.objects.create(name='Fixing Asphalt')
        self.team = ServiceTeam.objects.create(county=shemiran, speciality=self.asphalt_fixing)
        self.serviceman = Serviceman.objects.create(user=serviceman_user, team=self.team, lat=1, long=1)
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
        # postpone is not considered yet
        self.assertEqual(self.issue.state, Issue.State.FAILED)

    def test_assignment_successful(self):
        self.expert.accept_issue(self.issue, self.service_type, [(self.asphalt_fixing, 1)], [(self.crane_type, 3)])
        self.issue.refresh_from_db()
        self.team.refresh_from_db()
        self.crane.refresh_from_db()
        self.assertEqual(self.issue.state, Issue.State.ASSIGNED)
        self.assertEqual(self.serviceman.team.active_mission, self.issue.mission)
        self.assertEqual(self.crane.available_count, 7)


class SubmitIssueTestCase(TestCase):
    def setUp(self):
        self.citizen_user = User.objects.create(username='parsa', phone_number='0')
        self.citizen = Citizen.objects.create(user=self.citizen_user)

        self.iran = Country.objects.create(name='Iran')
        self.tehran = Province.objects.create(name='Tehran', super_region=self.iran)
        self.tehran.refresh_from_db()
        self.shemiranat = County.objects.create(name='Shemiranat', super_region=self.tehran)
        self.shemiranat.refresh_from_db()

        self.expert_user = User.objects.create(username='kiarash', phone_number='1')
        self.expert = CountyExpert.objects.create(user=self.expert_user, county=self.shemiranat)

    def test_submit_issue(self):
        self.issue = self.citizen.submit_issue(title='The cow on the road',
                                               description='There is a cow trapped in the Chamran Highway guard rails!',
                                               county=self.shemiranat)
        self.assertTrue(self.issue in self.expert.county.issue_set.all())
        print(self.expert.get_reported_issues())

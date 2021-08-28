from django.test import TestCase
from accounts.models import User
from core.models import Country, Province, County, CountryModerator, ProvinceModerator, Citizen, Serviceman, \
    ServiceTeam, Speciality, CountyExpert, Issue, MachineryType, Machinery, MissionType, Location, Region


class BaseTestCase(TestCase):
    def setUpRegions(self):
        self.iran = Country.objects.create(name='Iran')

        self.tehran_province = Province.objects.create(name='Tehran (P)', super_region=self.iran.region_ptr)
        self.tehran_province.refresh_from_db()
        self.shiraz_province = Province.objects.create(name='Shiraz (P)', super_region=self.iran.region_ptr)
        self.shiraz_province.refresh_from_db()
        self.khorasan = Province.objects.create(name='Khorasan', super_region=self.iran.region_ptr)
        self.khorasan.refresh_from_db()
        self.isfahan_province = Province.objects.create(name='Isfahan (P)', super_region=self.iran.region_ptr)
        self.isfahan_province.refresh_from_db()

        self.tehran = County.objects.create(name='Tehran', super_region=self.tehran_province.region_ptr)
        self.tehran.refresh_from_db()
        self.damavand = County.objects.create(name='Damavand', super_region=self.tehran_province.region_ptr)
        self.damavand.refresh_from_db()
        self.shahrerey = County.objects.create(name='Shahrerey', super_region=self.tehran_province.region_ptr)
        self.shahrerey.refresh_from_db()
        self.shiraz = County.objects.create(name='Shiraz', super_region=self.shiraz_province.region_ptr)
        self.shiraz.refresh_from_db()
        self.marvdasht = County.objects.create(name='Marvdasht', super_region=self.shiraz_province.region_ptr)
        self.marvdasht.refresh_from_db()
        self.mashhad = County.objects.create(name='Mashhad', super_region=self.khorasan.region_ptr)
        self.mashhad.refresh_from_db()
        self.neyshabur = County.objects.create(name='Neyshabur', super_region=self.khorasan.region_ptr)
        self.neyshabur.refresh_from_db()
        self.isfahan = County.objects.create(name='Isfahan', super_region=self.isfahan_province.region_ptr)
        self.isfahan.refresh_from_db()
        self.khansar = County.objects.create(name='Khansar', super_region=self.isfahan_province.region_ptr)
        self.khansar.refresh_from_db()

    def setUpModerators(self):
        self.parsa = User.objects.create(username='parsa', phone_number='0')
        self.kiarash = User.objects.create(username='kiarash', phone_number='1')
        self.majid = User.objects.create(username='majid', phone_number='2')
        self.mahdi = User.objects.create(username='mahdi', phone_number='3')
        self.ali = User.objects.create(username='ali', phone_number='4')
        self.alireza = User.objects.create(username='alireza', phone_number='5')
        self.pooyan = User.objects.create(username='pooyan', phone_number='6')
        self.amirkasra = User.objects.create(username='amirkasra', phone_number='7')
        self.amoo = User.objects.create(username='amoo', phone_number='8')
        self.erfan = User.objects.create(username='erfan', phone_number='9')
        self.sina = User.objects.create(username='sina', phone_number='10')
        self.gorji = User.objects.create(username='gorji', phone_number='11')
        self.maleki = User.objects.create(username='maleki', phone_number='12')
        self.amin = User.objects.create(username='amin', phone_number='13')

        self.iran_moderator = CountryModerator.objects.create(user=self.parsa, region=self.iran.region_ptr)
        self.iran.refresh_from_db()

        self.tehran_province_moderator = self.iran_moderator.assign_moderator(self.kiarash, self.tehran_province.region_ptr)
        self.tehran_moderator = self.tehran_province_moderator.assign_moderator(self.pooyan, self.tehran.region_ptr)
        self.damavand_moderator = self.tehran_province_moderator.assign_moderator(self.amirkasra, self.damavand.region_ptr)
        self.shahrerey_moderator = self.tehran_province_moderator.assign_moderator(self.majid, self.shahrerey.region_ptr)

        self.shiraz_province_moderator = self.iran_moderator.assign_moderator(self.mahdi, self.shiraz_province.region_ptr)
        self.shiraz_moderator = self.shiraz_province_moderator.assign_moderator(self.amin, self.shiraz.region_ptr)
        self.marvdasht_moderator = self.shiraz_province_moderator.assign_moderator(self.ali, self.marvdasht.region_ptr)

        self.khorasan_moderator = self.iran_moderator.assign_moderator(self.maleki, self.khorasan.region_ptr)
        self.mashhad_moderator = self.khorasan_moderator.assign_moderator(self.gorji, self.mashhad.region_ptr)
        self.neyshabur_moderator = self.khorasan_moderator.assign_moderator(self.alireza, self.neyshabur.region_ptr)

        self.isfahan_province_moderator = self.iran_moderator.assign_moderator(self.sina, self.isfahan_province.region_ptr)
        self.isfahan_moderator = self.isfahan_province_moderator.assign_moderator(self.erfan, self.isfahan.region_ptr)
        self.khansar_moderator = self.isfahan_province_moderator.assign_moderator(self.amoo, self.khansar.region_ptr)

    def setUpExperts(self):
        self.akbar = User.objects.create(username='akbar', phone_number='14')
        self.sajad = User.objects.create(username='sajad', phone_number='15')
        self.armin = User.objects.create(username='armin', phone_number='16')
        self.hadi = User.objects.create(username='hadi', phone_number='17')
        self.reza = User.objects.create(username='reza', phone_number='18')
        self.aria = User.objects.create(username='aria', phone_number='19')
        self.hassan = User.objects.create(username='hassan', phone_number='20')
        self.kianoosh = User.objects.create(username='kianoosh', phone_number='21')
        self.elyas = User.objects.create(username='elyas', phone_number='22')

        self.tehran_expert = CountyExpert.objects.create(user=self.armin, county=self.tehran)
        self.damavand_expert = CountyExpert.objects.create(user=self.aria, county=self.damavand)
        self.shahrerey_expert = CountyExpert.objects.create(user=self.akbar, county=self.shahrerey)
        self.shiraz_expert = CountyExpert.objects.create(user=self.hadi, county=self.shiraz)
        self.marvdasht_expert = CountyExpert.objects.create(user=self.sajad, county=self.marvdasht)
        self.mashhad_expert = CountyExpert.objects.create(user=self.reza, county=self.mashhad)
        self.neyshabur_expert = CountyExpert.objects.create(user=self.kianoosh, county=self.neyshabur)
        self.isfahan_expert = CountyExpert.objects.create(user=self.hassan, county=self.isfahan)
        self.khansar_expert = CountyExpert.objects.create(user=self.elyas, county=self.khansar)

    def setUpCitizens(self):
        self.hamid = User.objects.create(username='hamid', phone_number='23')
        self.moein = User.objects.create(username='moein', phone_number='24')
        self.milad = User.objects.create(username='milad', phone_number='25')
        self.soroush = User.objects.create(username='soroush', phone_number='26')
        self.farbod = User.objects.create(username='farbod', phone_number='27')
        self.hossein = User.objects.create(username='hossein', phone_number='28')
        self.mohammad = User.objects.create(username='mohammad', phone_number='29')

        self.citizen0 = Citizen.objects.create(user=self.hamid)
        self.citizen1 = Citizen.objects.create(user=self.moein)
        self.citizen2 = Citizen.objects.create(user=self.milad)
        self.citizen3 = Citizen.objects.create(user=self.soroush)
        self.citizen4 = Citizen.objects.create(user=self.farbod)
        self.citizen5 = Citizen.objects.create(user=self.hossein)
        self.citizen6 = Citizen.objects.create(user=self.mohammad)

    def setUpSpecialities(self):
        self.water_speciality = Speciality.objects.create(name='Water')
        self.wind_speciality = Speciality.objects.create(name='Wind')
        self.moon_speciality = Speciality.objects.create(name='Moon')
        self.sun_speciality = Speciality.objects.create(name='Sun')
        self.sky_speciality = Speciality.objects.create(name='Sky')

    def setUpMachineryTypes(self):
        self.crane_type = MachineryType.objects.create(name='Crane')
        self.loader_type = MachineryType.objects.create(name='Loader')
        self.truck_type = MachineryType.objects.create(name='Truck')
        self.ambulance_type = MachineryType.objects.create(name='Ambulance')
        self.firetruck_type = MachineryType.objects.create(name='Fire Truck')

    def setUpMissionTypes(self):
        self.road_type = MissionType.objects.create(name='Road')
        self.fire_type = MissionType.objects.create(name='Fire')
        self.animal_type = MissionType.objects.create(name='Animal')
        self.water_type = MissionType.objects.create(name='Water')

    def setUpMachineries(self):
        Machinery.objects.create(type=self.crane_type, county=self.tehran, total_count=100, available_count=100)
        Machinery.objects.create(type=self.loader_type, county=self.tehran, total_count=50, available_count=50)
        Machinery.objects.create(type=self.truck_type, county=self.tehran, total_count=30, available_count=30)
        Machinery.objects.create(type=self.ambulance_type, county=self.tehran, total_count=40, available_count=40)
        Machinery.objects.create(type=self.firetruck_type, county=self.tehran, total_count=30, available_count=30)

        Machinery.objects.create(type=self.crane_type, county=self.shiraz, total_count=80, available_count=80)
        Machinery.objects.create(type=self.loader_type, county=self.shiraz, total_count=30, available_count=30)
        Machinery.objects.create(type=self.truck_type, county=self.shiraz, total_count=15, available_count=15)
        Machinery.objects.create(type=self.ambulance_type, county=self.shiraz, total_count=20, available_count=20)
        Machinery.objects.create(type=self.firetruck_type, county=self.shiraz, total_count=15, available_count=15)

        Machinery.objects.create(type=self.crane_type, county=self.mashhad, total_count=90, available_count=70)
        Machinery.objects.create(type=self.loader_type, county=self.mashhad, total_count=40, available_count=30)
        Machinery.objects.create(type=self.truck_type, county=self.mashhad, total_count=25, available_count=25)
        Machinery.objects.create(type=self.ambulance_type, county=self.mashhad, total_count=30, available_count=30)
        Machinery.objects.create(type=self.firetruck_type, county=self.mashhad, total_count=20, available_count=20)

        Machinery.objects.create(type=self.crane_type, county=self.isfahan, total_count=80, available_count=50)
        Machinery.objects.create(type=self.loader_type, county=self.isfahan, total_count=50, available_count=40)
        Machinery.objects.create(type=self.truck_type, county=self.isfahan, total_count=25, available_count=25)
        Machinery.objects.create(type=self.ambulance_type, county=self.isfahan, total_count=35, available_count=30)
        Machinery.objects.create(type=self.firetruck_type, county=self.isfahan, total_count=25, available_count=20)

    def setUpTeams(self):
        self.u0 = User.objects.create(username='u0', phone_number='30')
        self.u1 = User.objects.create(username='u1', phone_number='31')
        self.u2 = User.objects.create(username='u2', phone_number='32')
        self.tehran_water_team0 = ServiceTeam.objects.create(county=self.tehran, speciality=self.water_speciality)
        self.tehran_water_team0_servicemen = [Serviceman.objects.create(user=self.u0, team=self.tehran_water_team0, lat=1, long=1),
        Serviceman.objects.create(user=self.u1, team=self.tehran_water_team0, lat=1.1, long=1),
        Serviceman.objects.create(user=self.u2, team=self.tehran_water_team0, lat=1, long=1.1)]

        self.u3 = User.objects.create(username='u3', phone_number='33')
        self.u4 = User.objects.create(username='u4', phone_number='34')
        self.tehran_water_team1 = ServiceTeam.objects.create(county=self.tehran, speciality=self.water_speciality)
        self.tehran_water_team1_servicemen = [Serviceman.objects.create(user=self.u3, team=self.tehran_water_team1, lat=1, long=1),
        Serviceman.objects.create(user=self.u4, team=self.tehran_water_team1, lat=1.5, long=1)]

        self.u5 = User.objects.create(username='u5', phone_number='35')
        self.u6 = User.objects.create(username='u6', phone_number='36')
        self.tehran_wind_team = ServiceTeam.objects.create(county=self.tehran, speciality=self.wind_speciality)
        self.tehran_wind_team_servicemen = [Serviceman.objects.create(user=self.u5, team=self.tehran_wind_team, lat=1.1, long=1.2),
        Serviceman.objects.create(user=self.u6, team=self.tehran_wind_team, lat=1.5, long=1.3)]

        self.tehran_moon_team0 = ServiceTeam.objects.create(county=self.tehran, speciality=self.moon_speciality)
        self.tehran_moon_team1 = ServiceTeam.objects.create(county=self.tehran, speciality=self.moon_speciality)
        self.tehran_sun_team = ServiceTeam.objects.create(county=self.tehran, speciality=self.sun_speciality)
        self.tehran_sky_team = ServiceTeam.objects.create(county=self.tehran, speciality=self.sky_speciality)

        self.shiraz_water_team = ServiceTeam.objects.create(county=self.shiraz, speciality=self.water_speciality)
        self.shiraz_wind_team = ServiceTeam.objects.create(county=self.shiraz, speciality=self.wind_speciality)
        self.shiraz_moon_team = ServiceTeam.objects.create(county=self.shiraz, speciality=self.moon_speciality)
        self.shiraz_sun_team0 = ServiceTeam.objects.create(county=self.shiraz, speciality=self.sun_speciality)
        self.shiraz_sun_team1 = ServiceTeam.objects.create(county=self.shiraz, speciality=self.sun_speciality)
        self.shiraz_sun_team2 = ServiceTeam.objects.create(county=self.shiraz, speciality=self.sun_speciality)

        self.isfahan_water_team0 = ServiceTeam.objects.create(county=self.isfahan, speciality=self.water_speciality)
        self.isfahan_water_team1 = ServiceTeam.objects.create(county=self.isfahan, speciality=self.water_speciality)
        self.isfahan_wind_team0 = ServiceTeam.objects.create(county=self.isfahan, speciality=self.wind_speciality)
        self.isfahan_wind_team1 = ServiceTeam.objects.create(county=self.isfahan, speciality=self.wind_speciality)

        self.mashhad_moon_team = ServiceTeam.objects.create(county=self.mashhad, speciality=self.moon_speciality)
        self.mashhad_sun_team = ServiceTeam.objects.create(county=self.mashhad, speciality=self.sun_speciality)
        self.mashhad_sky_team = ServiceTeam.objects.create(county=self.mashhad, speciality=self.sky_speciality)

    def setUpIssues(self):
        self.issue0 = self.citizen0.submit_issue(title='The cow on the road',
                                                 description='There is a cow trapped in the Chamran Highway guard rails!',
                                                 county=self.tehran)
        self.issue1 = self.citizen1.submit_issue(title='Slippery road',
                                                 description='The road is slippery',
                                                 county=self.shahrerey)

    def setUp(self):
        self.setUpRegions()
        self.setUpModerators()
        self.setUpExperts()
        self.setUpCitizens()
        self.setUpSpecialities()
        self.setUpMachineryTypes()
        self.setUpMissionTypes()
        self.setUpMachineries()
        self.setUpTeams()
        self.setUpIssues()

class CitizenTestCase(BaseTestCase):
    def test_submit_issue(self):
        self.assertTrue(self.issue0 in self.issue0.county.issue_set.all())
        self.assertFalse(self.issue0 in self.issue1.county.issue_set.all())
        self.assertTrue(self.issue1 in self.issue1.county.issue_set.all())
        self.assertFalse(self.issue1 in self.issue0.county.issue_set.all())

        self.assertEqual(self.issue0.state, Issue.State.REPORTED)
        self.assertEqual(self.issue1.state, Issue.State.REPORTED)

    def test_view_issue(self):
        self.assertTrue(self.citizen0.can_view_issue(self.issue0))
        self.assertFalse(self.citizen0.can_view_issue(self.issue1))

    def test_rate_issue(self):
        self.mission = self.tehran_expert.accept_issue(self.issue0, self.animal_type, [(self.wind_speciality, 1)], [(self.crane_type, 1), (self.truck_type, 1)])
        self.tehran_wind_team.refresh_from_db()
        self.tehran_wind_team_servicemen[0].end_mission('The cow is caught alive')
        self.issue0.refresh_from_db()
        self.assertTrue(self.citizen0.rate_issue(self.issue0, 3))
        self.mission.refresh_from_db()
        self.assertEqual(self.mission.score, 3)
        self.assertEqual(self.issue0.state, Issue.State.SCORED)


class ServicemanTestCase(BaseTestCase):
    def test_update_location(self):
        serviceman = self.tehran_water_team0_servicemen[0]
        serviceman.update_location(Location(0, 0))
        new_location = Location(3.5, 7)
        serviceman.update_location(new_location)
        self.assertEqual(serviceman.location, new_location)

    def test_end_mission(self):
        service_team = self.tehran_wind_team
        crane_need = 2
        truck_need = 3
        self.mission = self.tehran_expert.accept_issue(self.issue0, self.animal_type, [(self.wind_speciality, 1)],
                                                       [(self.crane_type, crane_need), (self.truck_type, truck_need)])
        available_cranes = self.tehran.machinery_set.get(type=self.crane_type).available_count
        available_trucks = self.tehran.machinery_set.get(type=self.truck_type).available_count
        self.tehran_wind_team.refresh_from_db()
        self.tehran_wind_team_servicemen[0].end_mission('The cow is caught alive')
        self.issue0.refresh_from_db()
        self.assertEqual(self.issue0.state, Issue.State.DONE)
        self.tehran_wind_team.refresh_from_db()
        self.assertIsNone(self.tehran_wind_team.active_mission)
        self.assertEqual(available_cranes + crane_need, self.tehran.machinery_set.get(type=self.crane_type).available_count)
        self.assertEqual(available_trucks + truck_need, self.tehran.machinery_set.get(type=self.truck_type).available_count)


class CountyExpertTestCase(TestCase):
    def setUp(self):
        pass

    def test_get_reported_issues(self):
        pass

    def test_get_issues(self):
        pass

    def test_view_issue(self):
        pass
    
    def test_accept_issue(self):
        pass # check the commented code at the end of file

    def test_reject_issue(self):
        pass

    def test_get_mission_types(self):
        pass

    def test_add_mission_type(self):
        pass

    def test_rename_mission_type(self):
        pass

    def test_delete_mission_type(self):
        pass


class IssueTestCase(TestCase):
    def setUp(self):
        pass

    def test_assign_resources(self):
        pass


class ModeratorTestCase(BaseTestCase):
    def setUp(self):
        self.setUpRegions()
        self.setUpCitizens()
        self.parsa = User.objects.create(username='parsa', phone_number='0')
        self.kiarash = User.objects.create(username='kiarash', phone_number='1')
        self.majid = User.objects.create(username='majid', phone_number='2')
        self.mahdi = User.objects.create(username='mahdi', phone_number='3')

    def setUpModerators(self):
        self.iran_moderator = CountryModerator.objects.create(user=self.parsa, region=self.iran.region_ptr)
        self.tehran_province_moderator = self.iran_moderator.assign_moderator(self.kiarash, self.tehran_province.region_ptr)
        self.tehran_moderator = self.tehran_province_moderator.assign_moderator(self.majid, self.tehran.region_ptr)

    def setUpIssues(self):
        self.issue0 = self.citizen0.submit_issue(title='The cow on the road',
                                                 description='There is a cow trapped in the Chamran Highway guard rails!',
                                                 county=self.tehran)
        self.issue1 = self.citizen1.submit_issue(title='The horse on the road',
                                                 description='There is a horse trapped in the Chamran Highway guard rails!',
                                                 county=self.damavand)
        self.issue2 = self.citizen2.submit_issue(title='The fox on the road',
                                                 description='There is a fox trapped in the Chamran Highway guard rails!',
                                                 county=self.shiraz)

    def test_assign_moderator(self):
        self.iran_moderator = CountryModerator.objects.create(user=self.parsa, region=self.iran.region_ptr)
        self.iran.refresh_from_db()
        self.assertEqual(self.iran.moderator.user, self.parsa)
        tehran_province_moderator = self.iran_moderator.assign_moderator(self.kiarash, self.tehran_province.region_ptr)
        self.assertEqual(self.tehran_province.moderator.user, self.kiarash)
        tehran_province_moderator.assign_moderator(self.majid, self.damavand.region_ptr)
        self.assertEqual(self.damavand.moderator.user, self.majid)
        with self.assertRaisesMessage(Exception, 'The region is not in the moderator\'s subregions'):
            tehran_province_moderator.assign_moderator(self.mahdi, self.shiraz_province.region_ptr)
        with self.assertRaisesMessage(Exception, 'The user is already the moderator of the region'):
            self.iran_moderator.assign_moderator(self.kiarash, self.tehran_province.region_ptr)
        with self.assertRaisesMessage(Exception, 'The user has a role'):
            self.iran_moderator.assign_moderator(self.majid, self.shiraz_province.region_ptr)

        self.iran_moderator.assign_moderator(self.mahdi, self.tehran_province.region_ptr)
        self.kiarash.refresh_from_db()
        self.tehran_province.refresh_from_db()
        self.iran_moderator.assign_moderator(self.kiarash, self.shiraz_province.region_ptr)
        self.assertEqual(self.tehran_province.moderator.user, self.mahdi)
        self.assertEqual(self.shiraz_province.moderator.user, self.kiarash)

    def test_get_concrete(self):
        self.setUpModerators()
        self.assertEqual(self.iran_moderator.moderator_ptr.get_concrete(), self.iran_moderator)
        self.assertEqual(self.tehran_province_moderator.moderator_ptr.get_concrete(), self.tehran_province_moderator)
        self.assertEqual(self.tehran_moderator.moderator_ptr.get_concrete(), self.tehran_moderator)
        self.assertEqual(self.tehran_moderator.moderator_ptr.role_ptr.get_concrete(), self.tehran_moderator)

    def test_can_moderate(self):
        self.setUpModerators()
        self.assertTrue(self.iran_moderator.moderator_ptr.can_moderate(self.iran.region_ptr))
        self.assertTrue(self.iran_moderator.moderator_ptr.can_moderate(self.shiraz_province.region_ptr))
        self.assertTrue(self.iran_moderator.moderator_ptr.can_moderate(self.shiraz.region_ptr))
        self.assertTrue(self.tehran_province_moderator.moderator_ptr.can_moderate(self.tehran_province.region_ptr))
        self.assertTrue(self.tehran_province_moderator.moderator_ptr.can_moderate(self.tehran.region_ptr))
        self.assertTrue(self.tehran_province_moderator.moderator_ptr.can_moderate(self.damavand.region_ptr))
        self.assertFalse(self.tehran_province_moderator.can_moderate(self.shiraz_province.region_ptr))
        self.assertFalse(self.tehran_province_moderator.can_moderate(self.shiraz.region_ptr))
        self.assertFalse(self.tehran_moderator.can_moderate(self.tehran_province.region_ptr))

    def test_get_issues(self):
        self.setUpModerators()
        self.setUpIssues()
        self.assertEqual(list(self.tehran_moderator.get_issues([self.tehran])), [self.issue0])
        self.assertEqual(set(self.tehran_province_moderator.get_issues(
            [self.tehran.region_ptr, self.damavand.region_ptr, self.shahrerey.region_ptr])),
                         set([self.issue0, self.issue1]))
        self.assertEqual(set(self.iran_moderator.get_issues(
            [self.tehran_province.region_ptr, self.shiraz.region_ptr, self.khorasan.region_ptr])),
                         set([self.issue0, self.issue1, self.issue2]))
        self.assertEqual(set(self.iran_moderator.get_issues(
            [self.shiraz.region_ptr, self.khorasan.region_ptr])), set([self.issue2]))
        self.assertEqual(set(self.iran_moderator.get_issues([self.khorasan.region_ptr])), set([]))

    def test_view_issue(self):
        self.setUpModerators()
        self.setUpIssues()
        self.assertTrue(self.iran_moderator.can_view_issue(self.issue0))
        self.assertTrue(self.iran_moderator.can_view_issue(self.issue1))
        self.assertTrue(self.iran_moderator.can_view_issue(self.issue2))
        self.assertTrue(self.tehran_province_moderator.can_view_issue(self.issue0))
        self.assertTrue(self.tehran_province_moderator.can_view_issue(self.issue1))
        self.assertTrue(self.tehran_moderator.can_view_issue(self.issue0))
        self.assertFalse(self.tehran_province_moderator.can_view_issue(self.issue2))
        self.assertFalse(self.tehran_moderator.can_view_issue(self.issue1))
        self.assertFalse(self.tehran_moderator.can_view_issue(self.issue2))


class RegionTestCase(BaseTestCase):
    def test_has_moderator(self):
        self.assertTrue(self.shiraz.has_moderator())
        self.shiraz_moderator.delete()
        self.shiraz.refresh_from_db()
        self.assertFalse(self.shiraz.has_moderator())

    def test_get_concrete(self):
        self.assertEqual(self.iran.region_ptr.get_concrete(), self.iran)
        self.assertEqual(self.tehran_province.region_ptr.get_concrete(), self.tehran_province)
        self.assertEqual(self.tehran.region_ptr.get_concrete(), self.tehran)

    def test_get_including_regions(self):
        including_regions = self.iran.region_ptr.get_including_regions()
        self.assertEqual(list(including_regions), [self.iran.region_ptr])
        including_regions = self.tehran_province.region_ptr.get_including_regions()
        self.assertEqual(list(including_regions), [self.iran.region_ptr, self.tehran_province.region_ptr])
        including_regions = self.tehran.region_ptr.get_including_regions()
        self.assertEqual(list(including_regions), [self.iran.region_ptr, self.tehran_province.region_ptr, self.tehran.region_ptr])

    def test_get_counties(self):
        counties = self.mashhad.get_counties()
        self.assertEqual(list(counties), [self.mashhad])
        counties = self.khorasan.get_counties()
        self.assertEqual(set(counties), set([self.neyshabur, self.mashhad]))
        counties = self.iran.get_counties()
        self.assertEqual(set(counties), set([self.tehran, self.damavand, self.shahrerey, self.isfahan, self.khansar,
                                             self.shiraz, self.marvdasht, self.neyshabur, self.mashhad]))


# class AcceptIssueTestCase(TestCase):
#     def setUp(self):
#         iran = Country.objects.create(name='Iran')
#         tehran = Province.objects.create(name='Tehran', super_region=iran)
#         shemiran = County.objects.create(name='Shemiran', super_region=tehran)
#         serviceman_user = User.objects.create(username='serviceman', phone_number='0')
#         reporter_user = User.objects.create(username='reporter', phone_number='1')
#         expert_user = User.objects.create(username='expert', phone_number='2')
#         self.asphalt_fixing = Speciality.objects.create(name='Fixing Asphalt')
#         self.team = ServiceTeam.objects.create(county=shemiran, speciality=self.asphalt_fixing)
#         self.serviceman = Serviceman.objects.create(user=serviceman_user, team=self.team, lat=1, long=1)
#         reporter = Citizen.objects.create(user=reporter_user)
#         self.expert = CountyExpert.objects.create(user=expert_user, county=shemiran)
#         self.issue = Issue.objects.create(title='Asphalt needs fixing',
#                                           description='.',
#                                           reporter=reporter,
#                                           county=shemiran)
#         self.crane_type = MachineryType.objects.create(name='Crane')
#         self.crane = Machinery.objects.create(type=self.crane_type, county=shemiran, total_count=10, available_count=10)
#         self.service_type = MissionType.objects.create(name='Service')
#
#     def test_assignment_fail(self):
#         self.expert.accept_issue(self.issue, self.service_type, [(self.asphalt_fixing, 2)], [(self.crane_type, 15)])
#         # postpone is not considered yet
#         self.assertEqual(self.issue.state, Issue.State.FAILED)
#
#     def test_assignment_successful(self):
#         self.expert.accept_issue(self.issue, self.service_type, [(self.asphalt_fixing, 1)], [(self.crane_type, 3)])
#         self.issue.refresh_from_db()
#         self.team.refresh_from_db()
#         self.crane.refresh_from_db()
#         self.assertEqual(self.issue.state, Issue.State.ASSIGNED)
#         self.assertEqual(self.serviceman.team.active_mission, self.issue.mission)
#         self.assertEqual(self.crane.available_count, 7)

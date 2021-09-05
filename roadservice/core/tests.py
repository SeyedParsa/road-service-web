from django.test import TestCase

from accounts.models import User
from core.models import Country, Province, County, CountryModerator, Citizen, Serviceman, \
    ServiceTeam, CountyExpert, Issue, MachineryType, Machinery, MissionType, Speciality, Location
from core.exceptions import AccessDeniedError, OccupiedUserError, DuplicatedInfoError, BusyResourceError, \
    ResourceNotFoundError, IllegalOperationInStateError, InvalidArgumentError


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

        self.tehran_province_moderator = self.iran_moderator.assign_moderator(self.kiarash,
                                                                              self.tehran_province.region_ptr)
        self.tehran_moderator = self.tehran_province_moderator.assign_moderator(self.pooyan, self.tehran.region_ptr)
        self.damavand_moderator = self.tehran_province_moderator.assign_moderator(self.amirkasra,
                                                                                  self.damavand.region_ptr)
        self.shahrerey_moderator = self.tehran_province_moderator.assign_moderator(self.majid,
                                                                                   self.shahrerey.region_ptr)

        self.shiraz_province_moderator = self.iran_moderator.assign_moderator(self.mahdi,
                                                                              self.shiraz_province.region_ptr)
        self.shiraz_moderator = self.shiraz_province_moderator.assign_moderator(self.amin, self.shiraz.region_ptr)
        self.marvdasht_moderator = self.shiraz_province_moderator.assign_moderator(self.ali, self.marvdasht.region_ptr)

        self.khorasan_moderator = self.iran_moderator.assign_moderator(self.maleki, self.khorasan.region_ptr)
        self.mashhad_moderator = self.khorasan_moderator.assign_moderator(self.gorji, self.mashhad.region_ptr)
        self.neyshabur_moderator = self.khorasan_moderator.assign_moderator(self.alireza, self.neyshabur.region_ptr)

        self.isfahan_province_moderator = self.iran_moderator.assign_moderator(self.sina,
                                                                               self.isfahan_province.region_ptr)
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
        self.tehran_crane = Machinery.objects.create(type=self.crane_type, county=self.tehran, total_count=100, available_count=100)
        Machinery.objects.create(type=self.loader_type, county=self.tehran, total_count=50, available_count=50)
        self.tehran_truck = Machinery.objects.create(type=self.truck_type, county=self.tehran, total_count=30, available_count=30)
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
        self.tehran_water_team0_servicemen = [
            Serviceman.objects.create(user=self.u0, team=self.tehran_water_team0, lat=1, long=1),
            Serviceman.objects.create(user=self.u1, team=self.tehran_water_team0, lat=1.1, long=1),
            Serviceman.objects.create(user=self.u2, team=self.tehran_water_team0, lat=1, long=1.1)]

        self.u3 = User.objects.create(username='u3', phone_number='33')
        self.u4 = User.objects.create(username='u4', phone_number='34')
        self.tehran_water_team1 = ServiceTeam.objects.create(county=self.tehran, speciality=self.water_speciality)
        self.tehran_water_team1_servicemen = [
            Serviceman.objects.create(user=self.u3, team=self.tehran_water_team1, lat=1, long=1),
            Serviceman.objects.create(user=self.u4, team=self.tehran_water_team1, lat=1.5, long=1)]

        self.u5 = User.objects.create(username='u5', phone_number='35')
        self.u6 = User.objects.create(username='u6', phone_number='36')
        self.tehran_wind_team = ServiceTeam.objects.create(county=self.tehran, speciality=self.wind_speciality)
        self.tehran_wind_team_servicemen = [
            Serviceman.objects.create(user=self.u5, team=self.tehran_wind_team, lat=1.1, long=1.2),
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
                                                 county=self.tehran,
                                                 location=Location(1.5, 2), base64_image=None)
        self.issue1 = self.citizen1.submit_issue(title='Slippery road',
                                                 description='The road is slippery',
                                                 county=self.shahrerey,
                                                 location=Location(1.5, 1), base64_image=None)
        self.issue2 = self.citizen2.submit_issue(title='An Issue',
                                                 description='There is an issue',
                                                 county=self.tehran,
                                                 location=Location(2, 3), base64_image=None)
        self.issue3 = self.citizen3.submit_issue(title='An Issue in Shiraz',
                                                 description='There is an issue in shiraz',
                                                 county=self.shiraz,
                                                 location=Location(2, 3), base64_image=None)

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
    def test_sign_up(self):
        citizen = Citizen.sign_up('0919', 'salam1234', phone_number='0919', first_name='parsa', last_name='asrap')
        citizen.submit_issue(title='Test Issue', description='Just to test', county=self.tehran,
                             location=Location(1.5, 3), base64_image=None)

    def test_submit_issue(self):
        self.assertTrue(self.issue0 in self.issue0.county.issue_set.all())
        self.assertFalse(self.issue0 in self.issue1.county.issue_set.all())
        self.assertTrue(self.issue1 in self.issue1.county.issue_set.all())
        self.assertFalse(self.issue1 in self.issue0.county.issue_set.all())

        self.assertEqual(self.issue0.state, Issue.State.REPORTED)
        self.assertEqual(self.issue1.state, Issue.State.REPORTED)

    def test_rate_issue(self):
        self.mission = self.tehran_expert.accept_issue(self.issue0, self.animal_type, [(self.wind_speciality, 1)],
                                                       [(self.crane_type, 1), (self.truck_type, 1)])
        self.tehran_wind_team.refresh_from_db()
        self.tehran_wind_team_servicemen[0].end_mission('The cow is caught alive')
        self.issue0.refresh_from_db()
        self.citizen0.rate_issue(self.issue0, 3)
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
        self.assertEqual(available_cranes + crane_need,
                         self.tehran.machinery_set.get(type=self.crane_type).available_count)
        self.assertEqual(available_trucks + truck_need,
                         self.tehran.machinery_set.get(type=self.truck_type).available_count)


class CountyExpertTestCase(BaseTestCase):
    def test_get_reported_issues(self):
        self.assertEqual(set(self.tehran_expert.get_reported_issues()), set([self.issue0, self.issue2]))

    def test_get_issues(self):
        self.assertEqual(set(self.tehran_expert.get_issues()), set([self.issue0, self.issue2]))
        self.mission = self.tehran_expert.accept_issue(self.issue0, self.animal_type, [(self.wind_speciality, 1)],
                                                       [(self.crane_type, 1), (self.truck_type, 1)])
        self.tehran_wind_team.refresh_from_db()
        self.tehran_wind_team_servicemen[0].end_mission('The cow is caught alive')
        self.assertEqual(set(self.tehran_expert.get_issues()), set([self.issue0, self.issue2]))


    def test_accept_issue(self):
        self.mission = self.tehran_expert.accept_issue(self.issue0, self.animal_type, [(self.water_speciality, 2)],
                                                       [(self.crane_type, 10), (self.truck_type, 5)])
        self.issue0.refresh_from_db()
        self.tehran_water_team0.refresh_from_db()
        self.tehran_water_team1.refresh_from_db()
        self.tehran_crane.refresh_from_db()
        self.tehran_truck.refresh_from_db()
        self.assertEqual(self.issue0.state, Issue.State.ASSIGNED)
        self.assertEqual(self.tehran_water_team0.active_mission, self.issue0.mission)
        self.assertEqual(self.tehran_water_team1.active_mission, self.issue0.mission)
        self.assertEqual(self.tehran_crane.available_count, 90)
        self.assertEqual(self.tehran_truck.available_count, 25)

        self.tehran_expert.accept_issue(self.issue2, self.fire_type, [(self.wind_speciality, 2)], [(self.crane_type, 5)])
        self.issue1.refresh_from_db()
        self.assertEqual(self.issue2.state, Issue.State.FAILED)

        self.shiraz_expert.accept_issue(self.issue3, self.fire_type, [(self.water_speciality, 1)],
                                        [(self.crane_type, 5)])
        self.issue1.refresh_from_db()
        self.assertEqual(self.issue3.state, Issue.State.FAILED)

    def test_reject_issue(self):
        self.tehran_expert.reject_issue(self.issue0)
        self.assertEqual(self.issue0.state, Issue.State.REJECTED)

    def test_manipulate_mission_types(self):
        self.tehran_expert.delete_mission_type(self.water_type)
        self.mashhad_expert.delete_mission_type(self.road_type)
        self.isfahan_expert.delete_mission_type(self.fire_type)
        self.shiraz_expert.delete_mission_type(self.animal_type)
        m1 = self.tehran_expert.add_mission_type('impossible 1')
        m2 = self.tehran_expert.add_mission_type('impossible 2')
        m3 = self.tehran_expert.add_mission_type('impossible 3')
        self.assertEqual(set(self.tehran_expert.get_mission_types()), set([m1, m2, m3]))
        self.tehran_expert.rename_mission_type(m1, 'possible')
        m1.refresh_from_db()
        self.assertEqual(m1.name, 'possible')
        self.tehran_expert.delete_mission_type(m3)
        self.assertEqual(set(self.tehran_expert.get_mission_types()), set([m1, m2]))

    def test_notify(self):
        pass  # test manually

class IssueTestCase(TestCase):
    def setUp(self):
        pass

    def test_assign_resources(self):
        pass

    def test_postpone_assignment(self):
        pass

    def test_rate(self):
        pass

    def test_return_machineries(self):
        pass


class ModeratorTestCase(BaseTestCase):
    def setUp(self):
        self.setUpRegions()
        self.setUpCitizens()
        self.parsa = User.objects.create(username='parsa', phone_number='0')
        self.kiarash = User.objects.create(username='kiarash', phone_number='1')
        self.majid = User.objects.create(username='majid', phone_number='2')
        self.mahdi = User.objects.create(username='mahdi', phone_number='3')

        self.osama = User.objects.create(username='osama', phone_number='021')
        self.osama.refresh_from_db()
        self.vladimir = User.objects.create(username='vladimir', phone_number='051')
        self.vladimir.refresh_from_db()
        self.james = User.objects.create(username='james', phone_number='007')
        self.james.refresh_from_db()
        self.mohammadali = User.objects.create(username='mohammadali', phone_number='44')
        self.mohammadali.refresh_from_db()
        self.asghar = User.objects.create(username='asghar', phone_number='55')
        self.asghar.refresh_from_db()
        self.ebrahim = User.objects.create(username='ebrahim', phone_number='66')
        self.ebrahim.refresh_from_db()
        self.abubakr = User.objects.create(username='abubakr', phone_number='77')
        self.abubakr.refresh_from_db()
        self.gholamali = User.objects.create(username='gholamali', phone_number='88')
        self.gholamali.refresh_from_db()
        self.nagamuto = User.objects.create(username='nagamuto', phone_number='89')
        self.nagamuto.refresh_from_db()

    def setUpModerators(self):
        self.iran_moderator = CountryModerator.objects.create(user=self.parsa, region=self.iran.region_ptr)
        self.parsa.refresh_from_db()
        self.iran.refresh_from_db()
        self.iran_moderator.refresh_from_db()
        self.tehran_province_moderator = self.iran_moderator.assign_moderator(self.kiarash,
                                                                              self.tehran_province.region_ptr)
        self.tehran_moderator = self.tehran_province_moderator.assign_moderator(self.majid, self.tehran.region_ptr)
        self.shahrerey_moderator = self.tehran_province_moderator.assign_moderator(self.mohammadali,
                                                                                   self.shahrerey.region_ptr)

    def setUpIssues(self):
        self.issue0 = self.citizen0.submit_issue(title='The cow on the road',
                                                 description='There is a cow trapped in the Chamran Highway guard rails!',
                                                 county=self.tehran,
                                                 location=Location(1.5, 2), base64_image=None)
        self.issue1 = self.citizen1.submit_issue(title='The horse on the road',
                                                 description='There is a horse trapped in the Chamran Highway guard rails!',
                                                 county=self.damavand,
                                                 location=Location(1.1, 1.1), base64_image=None)
        self.issue2 = self.citizen2.submit_issue(title='The fox on the road',
                                                 description='There is a fox trapped in the Chamran Highway guard rails!',
                                                 county=self.shiraz,
                                                 location=Location(1, 2), base64_image=None)

    def test_assign_moderator(self):
        self.iran_moderator = CountryModerator.objects.create(user=self.parsa, region=self.iran.region_ptr)
        self.iran.refresh_from_db()
        self.assertEqual(self.iran.moderator.user, self.parsa)
        tehran_province_moderator = self.iran_moderator.assign_moderator(self.kiarash, self.tehran_province.region_ptr)
        self.assertEqual(self.tehran_province.moderator.user, self.kiarash)
        tehran_province_moderator.assign_moderator(self.majid, self.damavand.region_ptr)
        self.assertEqual(self.damavand.moderator.user, self.majid)
        with self.assertRaises(AccessDeniedError):
            tehran_province_moderator.assign_moderator(self.mahdi, self.iran.region_ptr)
        with self.assertRaises(AccessDeniedError):
            tehran_province_moderator.assign_moderator(self.mahdi, self.shiraz_province.region_ptr)
        with self.assertRaises(AccessDeniedError):
            tehran_province_moderator.assign_moderator(self.mahdi, self.marvdasht.region_ptr)
        with self.assertRaises(OccupiedUserError):
            self.iran_moderator.assign_moderator(self.kiarash, self.tehran_province.region_ptr)
        with self.assertRaises(OccupiedUserError):
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

    def test_manipulating_speciality(self):
        self.setUpModerators()
        shahrerey_moderator = self.shahrerey.moderator.get_concrete()
        speciality = self.shahrerey_moderator.add_speciality('barricade removal')
        speciality2 = self.shahrerey_moderator.add_speciality('sade mabar2')
        self.assertEqual(speciality.name, 'barricade removal')
        self.shahrerey_moderator.rename_speciality(speciality, 'sade mabar')
        speciality.refresh_from_db()
        self.assertEqual(speciality.name, 'sade mabar')
        with self.assertRaises(DuplicatedInfoError):
            self.shahrerey_moderator.add_speciality('sade mabar')
        with self.assertRaises(DuplicatedInfoError):
            self.shahrerey_moderator.rename_speciality(speciality2, 'sade mabar')
        self.shahrerey_moderator.delete_speciality(speciality)
        self.shahrerey_moderator.delete_speciality(speciality2)
        # makes sure that sade mabar has been deleted
        self.assertEqual(self.shahrerey_moderator.add_speciality('barricade removal').name, 'barricade removal')

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
        self.setUpExperts()
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
        self.setUpExperts()
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

    def getting_reports(self):
        pass

    def test_expert_assignment(self):
        self.setUpModerators()
        self.damavand_expert = CountyExpert.objects.create(user=self.asghar, county=self.damavand)
        self.akbar = User.objects.create(username='akbar', phone_number='4')
        self.assertEqual(self.damavand.expert.user, self.asghar)
        self.shahrerey.moderator.get_concrete().assign_expert(self.akbar)
        self.assertEqual(self.shahrerey.expert.user, self.akbar)
        self.assertEqual(self.shahrerey.has_expert(), True)
        with self.assertRaises(OccupiedUserError):
            self.shahrerey.moderator.get_concrete().assign_expert(self.akbar)

    def test_user_creation(self):
        self.setUpModerators()
        self.jfk = self.shahrerey.moderator.create_new_user('JohnFKennedy', 'LeeHarveyOswald', '+1 555', 'John',
                                                            'Kennedy')
        self.assertEqual(self.jfk.username, 'JohnFKennedy')
        with self.assertRaises(DuplicatedInfoError):
            self.shahrerey.moderator.create_new_user('JohnFKennedy', 'LeeHarveyOswald', '+98 21', 'John', 'Kennedy')

    def test_team_manipulation(self):
        self.setUpModerators()
        shahrerey_moderator = self.shahrerey.moderator.get_concrete()
        self.my_speciality = self.shahrerey_moderator.add_speciality('snow plow')
        self.team17 = self.shahrerey_moderator.add_service_team(self.my_speciality, [self.osama, self.vladimir])
        self.assertEqual(self.vladimir.role.get_concrete().team, self.team17)
        self.shahrerey_moderator.edit_service_team(self.team17, self.my_speciality, [self.osama, self.abubakr])
        self.abubakr.refresh_from_db()
        self.assertEqual(self.abubakr.role.get_concrete().team, self.team17)
        self.vladimir.refresh_from_db()
        self.assertFalse(self.vladimir.has_role())
        with self.assertRaises(OccupiedUserError):
            self.shahrerey.moderator.get_concrete().add_service_team(self.my_speciality, [self.nagamuto, self.osama])
        with self.assertRaises(OccupiedUserError):
            self.shahrerey.moderator.get_concrete().edit_service_team(self.team17, self.my_speciality,
                                                       [self.osama, self.vladimir, self.kiarash])
        #TODO: Mark team17 as busy on a mission and see that we can't delete it due to BusyResourceError
        self.shahrerey_moderator.delete_service_team(self.team17)
        self.osama.refresh_from_db()
        self.assertFalse(self.osama.has_role())

    def test_machinery_manipulation(self):
        self.setUpModerators()
        self.tractor_type = MachineryType.objects.create(name='Tractor')
        self.snow_plow_type = MachineryType.objects.create(name='Snow Plow')
        self.bulldozer_type = MachineryType.objects.create(name='Bulldozer')
        self.grader_type = MachineryType.objects.create(name='Grader')
        self.tractor = Machinery.objects.create(type=self.tractor_type, total_count=1, available_count=1,
                                                county=self.shahrerey)
        self.shahrerey.moderator.get_concrete().increase_machinery(self.tractor_type)
        self.tractor.refresh_from_db()
        self.assertEqual(self.tractor.total_count, 2)
        self.tractor.refresh_from_db()
        self.shahrerey.moderator.get_concrete().decrease_machinery(self.tractor_type)
        self.tractor.refresh_from_db()
        self.assertEqual(self.tractor.total_count, 1)
        self.snow_plow = self.shahrerey.moderator.get_concrete().increase_machinery(self.snow_plow_type)
        self.snow_plow.refresh_from_db()
        self.assertEqual(self.snow_plow.total_count, 1)
        self.bulldozer = self.shahrerey.moderator.get_concrete().increase_machinery(self.bulldozer_type)
        self.bulldozer.refresh_from_db()
        self.assertEqual(self.bulldozer.total_count, 1)
        self.assertEqual(self.bulldozer.available_count, 1)
        self.assertEqual(self.bulldozer.county.get_concrete(), self.shahrerey)
        self.shahrerey.moderator.get_concrete().decrease_machinery(self.bulldozer_type)
        with self.assertRaises(ResourceNotFoundError):
            self.shahrerey.moderator.get_concrete().decrease_machinery(self.bulldozer_type)


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
        self.assertEqual(list(including_regions),
                         [self.iran.region_ptr, self.tehran_province.region_ptr, self.tehran.region_ptr])

    def test_get_counties(self):
        counties = self.mashhad.get_counties()
        self.assertEqual(list(counties), [self.mashhad])
        counties = self.khorasan.get_counties()
        self.assertEqual(set(counties), set([self.neyshabur, self.mashhad]))
        counties = self.iran.get_counties()
        self.assertEqual(set(counties), set([self.tehran, self.damavand, self.shahrerey, self.isfahan, self.khansar,
                                             self.shiraz, self.marvdasht, self.neyshabur, self.mashhad]))


class ScenarioTestCase1(BaseTestCase):
    def test_damavand(self):
        self.varamin = County.objects.create(name='Varamin', super_region=self.tehran_province.region_ptr)
        self.varamin.refresh_from_db()
        self.bouazar = User.objects.create(username='bouazar', phone_number='91')
        self.kareem = User.objects.create(username='kareem', phone_number='92')
        self.bouazar.refresh_from_db()
        self.varamin_moderator = self.tehran_province_moderator.assign_moderator(self.bouazar,
                                                                                  self.varamin.region_ptr)
        self.varamin_moderator.refresh_from_db()
        self.varamin_expert = self.varamin_moderator.get_concrete().assign_expert(self.kareem)
        self.roadroller_type = MachineryType.objects.create(name='Road Roller')
        self.roadroller = Machinery.objects.create(type=self.roadroller_type, total_count=1, available_count=1,
                                                county=self.varamin)
        self.varamin_moderator.get_concrete().increase_machinery(self.roadroller_type)
        self.varamin_moderator.get_concrete().increase_machinery(self.roadroller_type)
        self.varamin_moderator.get_concrete().decrease_machinery(self.roadroller_type)
        self.roadroller.refresh_from_db()
        self.assertEqual(self.roadroller.total_count, 2)
        # TODO: Insert some issue manipulation here and at its midst, manipulate teams and machinery
        # TODO: and make sure that everything's okay

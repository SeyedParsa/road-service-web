from abc import abstractmethod

from geopy.distance import geodesic
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from accounts.models import User, Role


class Location:
    def __init__(self, lat, long):
        self.lat = lat
        self.long = long

    def distance_from(self, location):
        return geodesic(self.to_tuple(), location.to_tuple()).miles

    def to_tuple(self):
        return self.lat, self.long


class GeoModel(models.Model):
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    long = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def location(self):
        return Location(self.lat, self.long)

    @location.setter
    def location(self, val):
        self.lat = val.lat
        self.long = val.long


class Region(models.Model):
    class Type(models.TextChoices):
        COUNTRY = 'CR'
        PROVINCE = 'PR'
        COUNTY = 'CY'

    type = models.CharField(max_length=2, choices=Type.choices)
    name = models.CharField(max_length=20)
    super_region = models.ForeignKey('self', related_name='sub_regions', null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def has_moderator(self):
        return hasattr(self, 'moderator')


class Country(Region):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Region.Type.COUNTRY


class Province(Region):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Region.Type.PROVINCE


class County(Region):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Region.Type.COUNTY

    def get_required_teams(self, speciality, amount, location):
        special_teams = list(
            self.serviceteam_set.filter(
                speciality=speciality,
                active_mission__isnull=True,
                deleted_at__isnull=True
            )
        )
        special_teams.sort(key=lambda t: t.farthest_member_distance(location))
        return special_teams[:amount]

    def get_required_machinery(self, machinery_type, amount):
        machinery_qs = self.machinery_set.filter(
            type=machinery_type,
            available_count__gte=amount
        )
        if not machinery_qs:
            return None
        return machinery_qs.get()


class Moderator(Role):
    region = models.OneToOneField(Region, on_delete=models.PROTECT)

    def __str__(self):
        return ' '.join([str(self.user), str(self.region)])

    def pre_assign_moderator(self, user, region):
        if region.region_ptr not in self.region.sub_regions.all():
            raise Exception('The region is not in the moderator\'s subregions')
        elif region.has_moderator() and region.moderator.user is user:
            raise Exception('The user is already the moderator of the region')
        elif user.has_role():
            raise Exception('The user has a role')
        elif region.has_moderator():
            region.moderator.delete()


class CountryModerator(Moderator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Role.Type.COUNTRY_MODERATOR

    @property
    def country(self):
        return self.region

    def assign_moderator(self, user, region):
        self.pre_assign_moderator(user, region)
        return ProvinceModerator.objects.create(user=user, region=region)


class ProvinceModerator(Moderator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Role.Type.PROVINCE_MODERATOR

    @property
    def province(self):
        return self.region

    def assign_moderator(self, user, region):
        self.pre_assign_moderator(user, region)
        return CountyModerator.objects.create(user=user, region=region)


class CountyModerator(Moderator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Role.Type.COUNTY_MODERATOR

    @property
    def county(self):
        return self.region

    # TODO
    def assign_county_expert(self):
        pass


class Speciality(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class ServiceTeam(models.Model):
    county = models.ForeignKey(County, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    deleted_at = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    active_mission = models.ForeignKey('Mission', on_delete=models.SET_NULL, null=True, blank=True)
    speciality = models.ForeignKey(Speciality, on_delete=models.PROTECT)

    def __str__(self):
        return '%s - %s (%d members)' % (self.speciality, self.county, len(self.members.all()))

    def farthest_member_distance(self, location):
        distances = [member.location.distance_from(location) for member in self.members.all()]
        return max(distances)


class Serviceman(Role, GeoModel):
    team = models.ForeignKey(ServiceTeam, on_delete=models.SET_NULL, null=True, related_name='members')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Role.Type.SERVICEMAN

    def update_location(self, location):
        self.location = location
        self.save()


class Citizen(Role):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Role.Type.CITIZEN


class MachineryType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Machinery(models.Model):
    type = models.ForeignKey(MachineryType, on_delete=models.PROTECT)
    county = models.ForeignKey(County, on_delete=models.CASCADE)
    total_count = models.PositiveIntegerField()
    available_count = models.PositiveIntegerField()

    def __str__(self):
        return '%s - %s: %d/%d' % (self.type, self.county, self.available_count, self.total_count)


class Issue(GeoModel):
    class State(models.TextChoices):
        REPORTED = 'RP'
        REJECTED = 'RJ'
        ACCEPTED = 'AC'
        FAILED = 'FL'
        ASSIGNED = 'AS'
        DONE = 'DO'
        SCORED = 'SC'

    title = models.CharField(max_length=50)
    description = models.CharField(max_length=280)
    reporter = models.ForeignKey(Citizen, on_delete=models.SET_NULL, null=True)
    county = models.ForeignKey(County, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    state = models.CharField(max_length=2, choices=State.choices, default=State.REPORTED)

    def __str__(self):
        return '%s: %s (%s)' % (self.county, self.title, self.State(self.state).label)

    def assign_resources(self, mission_type):
        # TODO: requires lock
        if self.state != Issue.State.ACCEPTED:
            raise Exception('The issues must be an accepted issue for resource assignment')
        required_teams = []
        for speciality_requirement in self.specialityrequirement_set.all():
            special_teams = self.county.get_required_teams(
                speciality_requirement.speciality,
                speciality_requirement.amount,
                self.location
            )
            if len(special_teams) < speciality_requirement.amount:
                self.postpone_assignment(mission_type)
                return
            required_teams += special_teams

        required_machineries = []
        for machinery_requirement in self.machineryrequirement_set.all():
            machinery = self.county.get_required_machinery(
                machinery_requirement.machinery_type,
                machinery_requirement.amount
            )
            if machinery is None:
                self.postpone_assignment(mission_type)
                return
            required_machineries.append((machinery, machinery_requirement.amount))

        mission = Mission.objects.create(issue=self, type=mission_type)
        for team in required_teams:
            mission.service_teams.add(team)
            team.active_mission = mission
            team.save()
        for machinery, amount in required_machineries:
            machinery.available_count -= amount
            machinery.save()
        self.state = Issue.State.ASSIGNED
        self.save()

    def postpone_assignment(self, mission_type):
        # Right now we won't implement the queue, so the mission will just fail
        self.state = Issue.State.FAILED
        self.save()


class SpecialityRequirement(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    speciality = models.ForeignKey(Speciality, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField()

    def __str__(self):
        return '%d x %s - %s: %s' % (self.amount, self.speciality, self.issue.county, self.issue.title)


class MachineryRequirement(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    machinery_type = models.ForeignKey(MachineryType, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField()

    def __str__(self):
        return '%d x %s - %s: %s' % (self.amount, self.machinery_type, self.issue.county, self.issue.title)


class MissionType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Mission(models.Model):
    issue = models.OneToOneField(Issue, on_delete=models.PROTECT)
    service_teams = models.ManyToManyField(ServiceTeam)
    type = models.ForeignKey(MissionType, on_delete=models.PROTECT)
    score = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    report = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.issue)

    @property
    def state(self):
        return self.issue.state

    @property
    def county(self):
        return self.issue.county

    @property
    def created_at_date(self):
        return self.issue.created_at.date()


class CountyExpert(Role):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Role.Type.COUNTY_EXPERT

    county = models.OneToOneField(County, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.user)

    def accept_issue(self, issue, mission_type, speciality_requirements, machinery_requirements):
        """
            speciality_requirements is a list of tuples in the form of (Speciality, Amount) in which the
                specialities are distinct. The same goes for machinery_requirements.
        """
        if issue.county is not self.county:
            raise Exception('The county expert can only accept the issues in its county')

        for speciality, amount in speciality_requirements:
            SpecialityRequirement.objects.create(issue=issue, speciality=speciality, amount=amount)

        for machinery_type, amount in machinery_requirements:
            MachineryRequirement.objects.create(issue=issue, machinery_type=machinery_type, amount=amount)

        issue.state = Issue.State.ACCEPTED
        issue.save()
        issue.assign_resources(mission_type)

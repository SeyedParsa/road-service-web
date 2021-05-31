from abc import abstractmethod

from geopy.distance import geodesic
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from accounts.models import User


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
    name = models.CharField(max_length=20)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Country(Region):
    pass


class Province(Region):
    country = models.ForeignKey(Country, on_delete=models.PROTECT)


class County(Region):
    province = models.ForeignKey(Province, on_delete=models.PROTECT)


class Moderator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def dismiss(self):
        self.user.state = User.State.SIMPLE
        self.user.save()
        self.delete()


class CountryModerator(Moderator):
    country = models.OneToOneField(Country, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.user.state = User.State.COUNTRY_MODERATOR
        self.user.save()
        super().save(*args, **kwargs)

    @classmethod
    def assign_province_moderator(cls, user, province):
        if hasattr(province, 'provincemoderator') and province.provincemoderator.user is user:
            raise Exception('The user is already the moderator of the province')
        elif user.has_role():
            raise Exception('The user has a role')
        else:
            if hasattr(province, 'provincemoderator'):
                province.provincemoderator.dismiss()
            return ProvinceModerator.objects.create(user=user, province=province)

    def __str__(self):
        return ' '.join([str(self.user), str(self.country)])


class ProvinceModerator(Moderator):
    province = models.OneToOneField(Province, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.user.state = User.State.PROVINCE_MODERATOR
        self.user.save()
        super().save(*args, **kwargs)

    @classmethod
    def assign_county_moderator(cls, user, county):
        if hasattr(county, 'countymoderator') and county.countymoderator.user is user:
            raise Exception('The user is already the moderator of the county')
        elif user.has_role():
            raise Exception('The user has a role')
        else:
            if hasattr(county, 'countymoderator'):
                county.countymoderator.dismiss()
            return CountyModerator.objects.create(user=user, county=county)

    def __str__(self):
        return ' '.join([str(self.user), str(self.province)])


class CountyModerator(Moderator):
    county = models.OneToOneField(County, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.user.state = User.State.COUNTY_MODERATOR
        self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return ' '.join([str(self.user), str(self.county)])


class Speciality(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


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


class ServiceTeam(models.Model):
    county = models.ForeignKey(County, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    deleted_at = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    active_mission = models.ForeignKey('Mission', on_delete=models.SET_NULL, null=True, blank=True)
    speciality = models.ForeignKey(Speciality, on_delete=models.PROTECT)

    def __str__(self):
        return '%s - %s (%d members)' % (self.speciality, self.county, len(self.members.all()))

    def farest_member_distance(self, location):
        distances = [member.location.distance_from(location) for member in self.members.all()]
        return max(distances)


class Serviceman(GeoModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey(ServiceTeam, on_delete=models.SET_NULL, null=True, related_name='members')

    def __str__(self):
        return str(self.user)


class Citizen(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


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

    def __str__(self):
        return str(self.issue)


class CountyExpert(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    county = models.OneToOneField(County, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    def accept_issue(self, issue, mission_type, speciality_requirements, machinery_requirements):
        """
            speciality_requirements is a list of tuples in the form of (Speciality, Amount) in which the
                specialities are distinct. The same goes for machinery_requirements.
        """
        for speciality, amount in speciality_requirements:
            SpecialityRequirement.objects.create(issue=issue, speciality=speciality, amount=amount)

        for machinery_type, amount in machinery_requirements:
            MachineryRequirement.objects.create(issue=issue, machinery_type=machinery_type, amount=amount)

        issue.state = Issue.State.ACCEPTED
        issue.save()
        self.assign_resources_to_issue(issue, mission_type)

    def assign_resources_to_issue(self, issue, mission_type):
        # TODO: requires lock
        # TODO: check if the issue is in the same county as the expert
        # TODO: check if the issue is the proper state (reported)
        required_teams = []
        for speciality_requirement in issue.specialityrequirement_set.all():
            service_team_qs = ServiceTeam.objects.filter(county=issue.county,
                                                         speciality=speciality_requirement.speciality,
                                                         active_mission__isnull=True,
                                                         deleted_at__isnull=True)
            special_teams = list(service_team_qs)
            if len(special_teams) < speciality_requirement.amount:
                self.postpone_assignment(issue, mission_type)
                return
            special_teams.sort(key=lambda t: t.farest_member_distance(issue.location))
            required_teams += special_teams[:speciality_requirement.amount]

        required_machineries = []
        for machinery_requirement in issue.machineryrequirement_set.all():
            machinery_qs = Machinery.objects.filter(county=issue.county,
                                                    type=machinery_requirement.machinery_type,
                                                    available_count__gte=machinery_requirement.amount)
            if not machinery_qs:
                self.postpone_assignment(issue, mission_type)
                return
            required_machineries.append((machinery_qs.get(), machinery_requirement.amount))

        mission = Mission.objects.create(issue=issue, type=mission_type)
        for team in required_teams:
            mission.service_teams.add(team)
            team.active_mission = mission
            team.save()
        for machinery, amount in required_machineries:
            machinery.available_count -= amount
            machinery.save()
        issue.state = Issue.State.ASSIGNED
        issue.save()

    def postpone_assignment(self, issue, mission_type):
        # Right now we won't implement the queue, so the mission will just fail
        issue.state = Issue.State.FAILED
        issue.save()

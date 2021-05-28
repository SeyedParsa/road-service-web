from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from accounts.models import User


class Province(models.Model):
    name = models.CharField(max_length=20)


class County(models.Model):
    name = models.CharField(max_length=20)
    province = models.ForeignKey(Province, on_delete=models.PROTECT)


class Speciality(models.Model):
    name = models.CharField(max_length=20)


class MachineryType(models.Model):
    name = models.CharField(max_length=20)


class Machinery(models.Model):
    type = models.ForeignKey(MachineryType, on_delete=models.PROTECT)
    county = models.ForeignKey(County, on_delete=models.CASCADE)
    total_count = models.PositiveIntegerField()
    available_count = models.PositiveIntegerField()


class ServiceTeam(models.Model):
    county = models.ForeignKey(County, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    deleted_at = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    active_mission = models.ForeignKey('Mission', on_delete=models.SET_NULL, null=True)
    speciality = models.ForeignKey(Speciality, on_delete=models.PROTECT)

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    @property
    def is_idle(self):
        return self.active_mission is None


class Serviceman(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(ServiceTeam, on_delete=models.SET_NULL, null=True)


class Citizen(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Location:
    def __init__(self, lat, long):
        self.lat = lat
        self.long = long


class Issue(models.Model):

    class IssueState(models.TextChoices):
        REPORTED = 'RP'
        REJECTED = 'RJ'
        ACCEPTED = 'AC'
        ASSIGNED = 'AS'
        DONE = 'DO'
        SCORED = 'SC'

    title = models.CharField(max_length=50)
    description = models.CharField(max_length=280)
    reporter = models.ForeignKey(Citizen, on_delete=models.SET_NULL, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    long = models.DecimalField(max_digits=9, decimal_places=6)
    province = models.ForeignKey(Province, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    state = models.CharField(max_length=2, choices=IssueState.choices, default=IssueState.REPORTED)

    @property
    def location(self):
        return Location(self.lat, self.long)

    @location.setter
    def location(self, val):
        self.lat = val.lat
        self.long = val.long


class SpecialityRequirement(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    speciality = models.ForeignKey(Speciality, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField()


class MachineryRequirement(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    machinery_type = models.ForeignKey(MachineryType, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField()


class MissionType(models.Model):
    name = models.CharField(max_length=20)


class Mission(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.PROTECT)
    service_teams = models.ManyToManyField(ServiceTeam)
    type = models.ForeignKey(MissionType, on_delete=models.PROTECT)
    score = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)


class CountyExpert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    county = models.ForeignKey(County, on_delete=models.CASCADE)

    # def accept_issue(self, issue, speciality_requirement_dict, machinery_requirement_dict):
    #     pass

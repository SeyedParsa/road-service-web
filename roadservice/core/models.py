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

    def __str__(self):
        return str(self.to_tuple())

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Location):
            return self.lat == other.lat and self.long == other.long
        return False


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
    super_region = models.ForeignKey('self', related_name='sub_regions', null=True, blank=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    def has_moderator(self):
        return hasattr(self, 'moderator')

    def get_concrete(self):
        if self.type == Region.Type.COUNTRY:
            return self.country
        elif self.type == Region.Type.PROVINCE:
            return self.province
        elif self.type == Region.Type.COUNTY:
            return self.county

    def get_including_regions(self):
        """returns a queryset consisting of regions that include this region"""
        res = Region.objects.filter(pk=self.pk)
        if self.type != Region.Type.COUNTRY:
            res |= self.super_region.get_including_regions()
        return res

    def get_counties(self):
        concrete = self.get_concrete()
        if concrete.type == Region.Type.COUNTY:
            return County.objects.filter(pk=self.pk)
        res = County.objects.none()
        for region in self.sub_regions.all():
            res |= region.get_counties()
        return res


class Country(Region):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Region.Type.COUNTRY

    def get_concrete(self):
        return self


class Province(Region):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Region.Type.PROVINCE

    def get_concrete(self):
        return self


class County(Region):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Region.Type.COUNTY

    def get_concrete(self):
        return self

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

    def notify_expert(self):
        pass # TODO


class Moderator(Role):
    region = models.OneToOneField(Region, on_delete=models.PROTECT)

    def __str__(self):
        return ' '.join([str(self.user), str(self.region)])

    def pre_assign_moderator(self, user, region):
        """Check if the assignment is valid and dismiss the previous moderator if applicable.\

        Keyword arguments:
        user -- the User that becomes moderator
        region -- the Region that becomes moderated
        """
        if region not in self.region.sub_regions.all():
            raise Exception('The region is not in the moderator\'s subregions')
        elif region.has_moderator() and region.moderator.user == user:
            raise Exception('The user is already the moderator of the region')
        elif user.has_role():
            raise Exception('The user has a role')
        elif region.has_moderator():
            region.moderator.delete()
            region.refresh_from_db()

    def get_concrete(self):
        if self.type == Role.Type.COUNTRY_MODERATOR:
            return self.countrymoderator
        elif self.type == Role.Type.PROVINCE_MODERATOR:
            return self.provincemoderator
        elif self.type == Role.Type.COUNTY_MODERATOR:
            return self.countymoderator

    def can_moderate(self, region):
        return self.region in region.get_including_regions()

    def can_view_issue(self, issue):
        return self.can_moderate(issue.county.region_ptr)

    def get_issues(self, regions):
        """return a queryset containing issues of the regions list"""
        res = Issue.objects.none()
        for region in regions:
            if self.can_moderate(region):
                for county in region.get_counties():
                    res |= county.issue_set.all()
        return res


class CountryModerator(Moderator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Role.Type.COUNTRY_MODERATOR

    def assign_moderator(self, user, region):
        """Assign user as the moderator of country if applicable and return the created Role.

        Keyword arguments:
        user -- the User that becomes moderator
        region -- the Region that becomes moderated
        """
        self.pre_assign_moderator(user, region)
        province_moderator = ProvinceModerator.objects.create(user=user, region=region)
        province_moderator.refresh_from_db()
        region.refresh_from_db()
        user.refresh_from_db()
        return province_moderator

    def get_concrete(self):
        return self


class ProvinceModerator(Moderator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Role.Type.PROVINCE_MODERATOR

    def assign_moderator(self, user, region):
        """Assign user as the moderator of country if applicable and return the created Role.

        Keyword arguments:
        user -- the User that becomes moderator
        region -- the Region that becomes moderated
        """
        self.pre_assign_moderator(user, region)
        county_moderator = CountyModerator.objects.create(user=user, region=region)
        county_moderator.refresh_from_db()
        region.refresh_from_db()
        user.refresh_from_db()
        return county_moderator

    def get_concrete(self):
        return self


class CountyModerator(Moderator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Role.Type.COUNTY_MODERATOR

    # TODO
    def assign_county_expert(self):
        pass

    def get_concrete(self):
        return self


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

    def get_concrete(self):
        return self

    def update_location(self, location):
        self.location = location
        self.save()

    def end_mission(self, report):
        if self.team.active_mission is not None:
            return self.team.active_mission.finish(report)
        else:
            return False


class Citizen(Role):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Role.Type.CITIZEN

    def get_concrete(self):
        return self

    def submit_issue(self, title, description, county, location):
        issue = Issue.objects.create(title=title, description=description, reporter=self, county=county,
                                     location=location)
        issue.notify_expert()
        return issue

    def can_view_issue(self, issue):
        return issue.reporter == self

    def rate_issue(self, issue, rating):
        if issue.reporter == self:
            return issue.rate(rating)
        else:
            return False


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
    # image = models.ImageField() TODO

    def __str__(self):
        return '%s: %s (%s)' % (self.county, self.title, self.State(self.state).label)

    def assign_resources(self, mission_type):
        # TODO: requires lock
        if self.state != Issue.State.ACCEPTED:
            return None
            # raise Exception('The issues must be an accepted issue for resource assignment')
        required_teams = []
        for speciality_requirement in self.specialityrequirement_set.all():
            special_teams = self.county.get_required_teams(
                speciality_requirement.speciality,
                speciality_requirement.amount,
                self.location
            )
            if len(special_teams) < speciality_requirement.amount:
                self.postpone_assignment(mission_type)
                return None
            required_teams += special_teams

        required_machineries = []
        for machinery_requirement in self.machineryrequirement_set.all():
            machinery = self.county.get_required_machinery(
                machinery_requirement.machinery_type,
                machinery_requirement.amount
            )
            if machinery is None:
                self.postpone_assignment(mission_type)
                return None
            required_machineries.append((machinery, machinery_requirement.amount))

        mission = Mission.objects.create(issue=self, type=mission_type)
        for team in required_teams:
            mission.service_teams.add(team)
            team.active_mission = mission
            team.save()
        mission.save()
        for machinery, amount in required_machineries:
            machinery.available_count -= amount
            machinery.save()
        self.state = Issue.State.ASSIGNED
        self.save()
        return mission

    def postpone_assignment(self, mission_type):
        # Right now we won't implement the queue, so the mission will just fail
        self.state = Issue.State.FAILED
        self.save()

    def notify_expert(self):
        self.county.notify_expert()

    def rate(self, rating):
        if self.state == Issue.State.DONE:
            self.mission.score = rating
            self.mission.save()
            self.state = Issue.State.SCORED
            self.save()
            return True
        else:
            return False

    def return_machineries(self):
        for machinery_requirement in self.machineryrequirement_set.all():
            machinery = self.county.machinery_set.get(type=machinery_requirement.machinery_type)
            machinery.available_count += machinery_requirement.amount
            machinery.save()


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

    def return_machineries(self):
        self.issue.return_machineries()

    def finish(self, report):
        if self.issue.state == Issue.State.ASSIGNED:
            self.report = report
            self.save()
            self.issue.state = Issue.State.DONE
            self.issue.save()
            for team in self.service_teams.all():
                team.active_mission = None
                team.save()
            self.return_machineries()
            return True
        else:
            return False


class CountyExpert(Role):
    county = models.OneToOneField(County, on_delete=models.PROTECT, related_name='expert')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Role.Type.COUNTY_EXPERT

    def __str__(self):
        return str(self.user)

    def get_concrete(self):
        return self

    def accept_issue(self, issue, mission_type, speciality_requirements, machinery_requirements):
        """
            speciality_requirements is a list of tuples in the form of (Speciality, Amount) in which the
                specialities are distinct. The same goes for machinery_requirements.
        """
        if issue.county != self.county:
            return None
            # raise Exception('The county expert can only accept the issues in its county')

        if issue.state != Issue.State.REPORTED:
            return None

        for speciality, amount in speciality_requirements:
            SpecialityRequirement.objects.create(issue=issue, speciality=speciality, amount=amount)

        for machinery_type, amount in machinery_requirements:
            MachineryRequirement.objects.create(issue=issue, machinery_type=machinery_type, amount=amount)

        issue.state = Issue.State.ACCEPTED
        issue.save()
        return issue.assign_resources(mission_type)

    def reject_issue(self, issue):
        if self.county == issue.county:
            issue.state = Issue.State.REJECTED
            issue.save()
            return True
        return False

    def get_issues(self):
        return self.county.issue_set.all()

    def get_reported_issues(self):
        return self.county.issue_set.filter(state=Issue.State.REPORTED)

    @staticmethod
    def get_mission_types():
        return MissionType.objects.all()

    @staticmethod
    def add_mission_type(name):
        MissionType.objects.create(name=name)

    @staticmethod
    def rename_mission_type(mission_type, name):
        mission_type.name = name
        mission_type.save()

    @staticmethod
    def delete_mission_type(mission_type):
        mission_type.delete()

    def can_view_issue(self, issue):
        return self.county == issue.county

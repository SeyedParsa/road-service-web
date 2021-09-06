import base64
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.images import get_image_dimensions
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, IntegrityError
from django.db.models import ProtectedError
from django.utils import timezone
from geopy.distance import geodesic

from accounts.exceptions import WeakPasswordError
from accounts.models import User, Role
from core.exceptions import AccessDeniedError, OccupiedUserError, DuplicatedInfoError, BusyResourceError, \
    ResourceNotFoundError, IllegalOperationInStateError, InvalidArgumentError
from sms.models import SmsSender


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
    super_region = models.ForeignKey('self', related_name='sub_regions', null=True, blank=True,
                                     on_delete=models.PROTECT)

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        if self.type == Region.Type.COUNTRY:
            return 'کشور ' + self.name
        if self.type == Region.Type.PROVINCE:
            return 'استان ' + self.name
        if self.type == Region.Type.COUNTY:
            return 'شهرستان ' + self.name

    def has_moderator(self):
        return hasattr(self, 'moderator')

    def is_concrete(self):
        return self.__class__ != Region

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
        if self.super_region is not None:
            res |= self.super_region.get_including_regions()
        return res

    def get_included_regions(self):
        """returns a queryset consisting of regions below this region"""
        res = Region.objects.filter(pk=self.pk)
        for sub_region in self.sub_regions.all():
            res |= sub_region.get_included_regions()
        return res

    def get_counties(self):
        if not self.is_concrete():
            return self.get_concrete().get_counties()
        res = County.objects.none()
        for region in self.sub_regions.all():
            res |= region.get_concrete().get_counties()
        return res

    def get_teams(self):
        res = ServiceTeam.objects.none()
        for county in self.get_counties():
            res |= county.get_teams()
        return res

    def get_machineries(self):
        res = Machinery.objects.none()
        for county in self.get_counties():
            res |= county.get_machineries()
        return res

    def get_issues(self):
        res = Issue.objects.none()
        for county in self.get_counties():
            res |= county.get_issues()
        return res

    def get_missions(self):
        res = Mission.objects.none()
        for county in self.get_counties():
            res |= county.get_missions()
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

    def get_counties(self):
        return County.objects.filter(pk=self.pk)

    def get_teams(self):
        return self.serviceteam_set.filter(deleted_at__isnull=True)

    def get_machineries(self):
        return self.machinery_set.all()

    def get_issues(self):
        return self.issue_set.all()

    def get_missions(self):
        return Mission.objects.filter(issue__county=self)

    def get_required_teams(self, speciality, amount, location):
        special_teams = list(
            self.serviceteam_set.filter(
                speciality=speciality,
                active_mission__isnull=True,
                deleted_at__isnull=True,
                members__isnull=False
            ).distinct()
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

    def has_expert(self):
        return hasattr(self, 'expert')

    def notify_expert(self):
        self.expert.notify()


class Moderator(Role):
    region = models.OneToOneField(Region, on_delete=models.PROTECT)

    def __str__(self):
        return '%s %s %s' % (self.type, self.region, self.user)

    def pre_assign_moderator(self, user, region):
        """Check if the assignment is valid and dismiss the previous moderator if applicable.\

        Keyword arguments:
        user -- the User that becomes moderator
        region -- the Region that becomes moderated
        """
        if region not in self.region.sub_regions.all():
            raise AccessDeniedError()
        elif user.has_role():
            raise OccupiedUserError()
        elif region.has_moderator():
            region.moderator.delete()
            region.moderator.user.refresh_from_db()
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
                res |= region.get_issues()
        return res

    def get_teams(self, regions):
        res = ServiceTeam.objects.none()
        for region in regions:
            if self.can_moderate(region):
                res |= region.get_teams()
        return res

    def get_machineries(self, regions):
        res = Machinery.objects.none()
        for region in regions:
            if self.can_moderate(region):
                res |= region.get_machineries()
        return res

    def create_new_user(self, username, password, phone_number, first_name, last_name):
        try:
            validate_password(password)
            user = User.objects.create(username=username, phone_number=phone_number,
                                       first_name=first_name, last_name=last_name)
            user.set_password(password)
            user.save()
            return user
        except IntegrityError:
            raise DuplicatedInfoError()
        except ValidationError:
            raise WeakPasswordError()


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

    @property
    def county(self):
        return self.region.get_concrete()

    def get_concrete(self):
        return self

    def add_service_team(self, speciality, members_users):
        for user in members_users:
            if user.has_role():
                raise OccupiedUserError()
        team = ServiceTeam.objects.create(county=self.county, speciality=speciality)
        for user in members_users:
            Serviceman.objects.create(team=team, user=user)
            user.refresh_from_db()
        return team

    def edit_service_team(self, team, speciality, members_users):
        ex_members_users = [serviceman.user for serviceman in team.members.all()]
        for user in members_users:
            if user.has_role() and user not in ex_members_users:
                raise OccupiedUserError()
        for user in members_users:
            if not user.has_role():
                Serviceman.objects.create(user=user, team=team)
                user.refresh_from_db()
        for serviceman in team.members.all():
            if serviceman.user not in members_users:
                serviceman.delete()
                serviceman.user.refresh_from_db()
        team.speciality = speciality
        team.save()

    def delete_service_team(self, team):
        if team.active_mission is not None:
            raise BusyResourceError()
        for serviceman in team.members.all():
            serviceman.delete()
            serviceman.user.refresh_from_db()
        team.deleted_at = timezone.now()
        team.save()

    def add_speciality(self, name):
        if Speciality.objects.filter(name=name).exists():
            raise DuplicatedInfoError()
        return Speciality.objects.create(name=name)

    def rename_speciality(self, speciality, new_name):
        if Speciality.objects.filter(name=new_name).exists():
            raise DuplicatedInfoError()
        speciality.name = new_name
        speciality.save()

    def delete_speciality(self, speciality):
        try:
            speciality.delete()
        except ProtectedError:
            raise BusyResourceError()

    def pre_assign_expert(self, user):
        # Check whether the operation is valid and dismiss the previous expert
        if user.has_role():
            raise OccupiedUserError()
        elif self.county.has_expert():
            self.county.expert.delete()
            self.county.expert.user.refresh_from_db()
            self.county.refresh_from_db()

    def assign_expert(self, user):
        self.pre_assign_expert(user)
        expert = CountyExpert.objects.create(user=user, county=self.county)
        user.refresh_from_db()
        return expert

    def increase_machinery(self, machinery_type):
        if not Machinery.objects.filter(type=machinery_type, county=self.county).exists():
            return Machinery.objects.create(type=machinery_type, total_count=1, available_count=1, county=self.county)
        machinery = Machinery.objects.get(type=machinery_type, county=self.county)
        machinery.increase()
        return machinery

    def decrease_machinery(self, machinery_type):
        if not Machinery.objects.filter(type=machinery_type, county=self.county).exists():
            raise ResourceNotFoundError()
        machinery = Machinery.objects.get(type=machinery_type, county=self.county)
        machinery.decrease()


class Speciality(models.Model):
    name = models.CharField(max_length=20, unique=True)

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
    team = models.ForeignKey(ServiceTeam, on_delete=models.PROTECT, null=True, related_name='members')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Role.Type.SERVICEMAN

    def get_concrete(self):
        return self

    def update_location(self, location):
        self.location = location
        self.save()

    def end_mission(self, report):
        if self.team.active_mission is None:
            raise IllegalOperationInStateError()
        self.team.active_mission.finish(report)


class Citizen(Role):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Role.Type.CITIZEN

    def get_concrete(self):
        return self

    def submit_issue(self, title, description, county, location, base64_image):
        if base64_image:
            file_name, image_file = Issue.get_image_from_base64(base64_image)
            Issue.validate_image(image_file)
        issue = Issue.objects.create(title=title, description=description, reporter=self, county=county,
                                     location=location)
        if base64_image:
            issue.image.save(file_name, image_file)
        county.notify_expert()
        return issue

    def rate_issue(self, issue, rating):
        if issue.reporter != self:
            raise AccessDeniedError()
        issue.rate(rating)

    @classmethod
    def sign_up(cls, username, password, phone_number, first_name, last_name):
        try:
            # Removed due to lack of error handling in Android app
            # validate_password(password)
            user = User.objects.create(username=username, phone_number=phone_number,
                                       first_name=first_name, last_name=last_name)
            user.set_password(password)
            user.save()
            citizen = cls.objects.create(user=user)
            user.refresh_from_db()
            return citizen
        except IntegrityError:
            raise DuplicatedInfoError()
        except ValidationError:
            raise WeakPasswordError()


class MachineryType(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Machinery(models.Model):
    type = models.ForeignKey(MachineryType, on_delete=models.PROTECT)
    county = models.ForeignKey(County, on_delete=models.CASCADE)
    total_count = models.PositiveIntegerField()
    available_count = models.PositiveIntegerField()

    def __str__(self):
        return '%s - %s: %d/%d' % (self.type, self.county, self.available_count, self.total_count)

    def increase(self):
        self.total_count += 1
        self.available_count += 1
        self.save()

    def decrease(self):
        if self.available_count == 0:
            raise BusyResourceError()
        self.total_count -= 1
        self.available_count -= 1
        if self.total_count == 0:
            self.delete()
        else:
            self.save()


class Issue(GeoModel):
    class State(models.TextChoices):
        REPORTED = 'RP'
        REJECTED = 'RJ'
        ACCEPTED = 'AC'
        FAILED = 'FL'
        ASSIGNED = 'AS'
        DONE = 'DO'
        SCORED = 'SC'

    @staticmethod
    def validate_image(image):
        if image.size > settings.ISSUE_IMAGE_LIMIT_MB * 1024 * 1024:
            raise ValidationError("Images have size limit of %d megabytes" % settings.ISSUE_IMAGE_LIMIT_MB)
        width, height = get_image_dimensions(image)
        ratio = width / height
        if ratio < 0.5 or ratio > 1.75:
            raise ValidationError("Ratio of the images should be between 1 and 1.75")

    title = models.CharField(max_length=50)
    description = models.CharField(max_length=280)
    reporter = models.ForeignKey(Citizen, on_delete=models.SET_NULL, null=True)
    county = models.ForeignKey(County, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    state = models.CharField(max_length=2, choices=State.choices, default=State.REPORTED)
    image = models.ImageField(upload_to='issue-images/', validators=[validate_image.__func__], null=True, blank=True)

    def __str__(self):
        return '%s: %s (%s)' % (self.county, self.title, self.State(self.state).label)

    @staticmethod
    def get_image_from_base64(base64_image):
        format, imgstr = base64_image.split(';base64,')
        ext = format.split('/')[-1]
        image_file = ContentFile(base64.b64decode(imgstr))
        file_name = '%s.%s' % (uuid4().hex, ext)
        return file_name, image_file

    def assign_resources(self, mission_type):
        # TODO: lock is required when manipulating resources (in this & other methods)
        if self.state != Issue.State.ACCEPTED:
            raise IllegalOperationInStateError()

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

        for machinery, amount in required_machineries:
            machinery.available_count -= amount
            machinery.save()
        self.state = Issue.State.ASSIGNED
        self.save()
        return mission

    def postpone_assignment(self, mission_type):
        # Right now we won't implement the queue, so the mission will just fail
        if self.state != Issue.State.ACCEPTED:
            raise IllegalOperationInStateError()
        self.state = Issue.State.FAILED
        self.save()

    def rate(self, rating):
        if self.state != Issue.State.DONE:
            raise IllegalOperationInStateError()
        self.mission.score = rating
        self.mission.save()
        self.state = Issue.State.SCORED
        self.save()

    def return_machineries(self):
        if self.state != Issue.State.DONE:
            raise IllegalOperationInStateError()
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
        if self.issue.state != Issue.State.ASSIGNED:
            raise IllegalOperationInStateError()
        self.report = report
        self.save()
        self.issue.state = Issue.State.DONE
        self.issue.save()
        for team in self.service_teams.all():
            team.active_mission = None
            team.save()
        self.return_machineries()


class CountyExpert(Role):
    county = models.OneToOneField(County, on_delete=models.PROTECT, related_name='expert')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = Role.Type.COUNTY_EXPERT

    def __str__(self):
        return '%s: %s' % (self.county, self.user)

    def get_concrete(self):
        return self

    def accept_issue(self, issue, mission_type, speciality_requirements, machinery_requirements):
        """
            speciality_requirements is a list of tuples in the form of (Speciality, Amount) in which the
                specialities are distinct. The same goes for machinery_requirements.
        """
        if issue.county != self.county:
            raise AccessDeniedError()

        if issue.state != Issue.State.REPORTED:
            raise IllegalOperationInStateError()

        requires_speciality = False
        for speciality, amount in speciality_requirements:
            if amount > 0:
                SpecialityRequirement.objects.create(issue=issue, speciality=speciality, amount=amount)
                requires_speciality = True

        if not requires_speciality:
            raise InvalidArgumentError()

        for machinery_type, amount in machinery_requirements:
            if amount > 0:
                MachineryRequirement.objects.create(issue=issue, machinery_type=machinery_type, amount=amount)

        issue.state = Issue.State.ACCEPTED
        issue.save()
        return issue.assign_resources(mission_type)

    def reject_issue(self, issue):
        if self.county != issue.county:
            raise IllegalOperationInStateError()
        if issue.state != Issue.State.REPORTED:
            raise IllegalOperationInStateError()
        issue.state = Issue.State.REJECTED
        issue.save()

    def notify(self):
        sms_sender = SmsSender.get_instance()
        message = 'مشکل تازه‌ای در شهرستان %s گزارش شده است. لطفا آن را بررسی فرمایید.' % self.county
        sms_sender.send_to_number(self.user.phone_number, message)

    def get_issues(self):
        return self.county.issue_set.all()

    def can_view_issue(self, issue):
        return self.county == issue.county

    def get_reported_issues(self):
        return self.county.issue_set.filter(state=Issue.State.REPORTED)

    def add_mission_type(self, name):
        if MissionType.objects.filter(name=name).exists():
            raise DuplicatedInfoError()
        return MissionType.objects.create(name=name)

    def rename_mission_type(self, mission_type, new_name):
        if MissionType.objects.filter(name=new_name).exists():
            raise DuplicatedInfoError()
        mission_type.name = new_name
        mission_type.save()

    def delete_mission_type(self, mission_type):
        try:
            mission_type.delete()
        except ProtectedError:
            raise BusyResourceError()

    def get_teams(self):
        return self.county.get_teams()

    def get_machineries(self):
        return self.county.get_machineries()

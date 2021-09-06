from rest_framework import serializers

from accounts.models import User
from accounts.serializers import UserSerializer
from core.models import Speciality, SpecialityRequirement, Issue, MachineryRequirement, MachineryType, MissionType, \
    Serviceman, Mission, County, Province, Country, ServiceTeam


class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Speciality
        fields = ['id', 'name']


class MachineryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineryType
        fields = ['id', 'name']


class MissionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionType
        fields = ['id', 'name']


class SpecialityRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialityRequirement
        fields = ['id', 'speciality', 'amount']


class MachineryRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineryRequirement
        fields = ['id', 'machinery_type', 'amount']


class IssueAcceptanceSerializer(serializers.Serializer):
    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all())
    mission_type = serializers.PrimaryKeyRelatedField(queryset=MissionType.objects.all())
    speciality_requirements = serializers.ListField(child=SpecialityRequirementSerializer())
    machinery_requirements = serializers.ListField(child=MachineryRequirementSerializer())


class IssueRejectionSerializer(serializers.Serializer):
    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all())


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serviceman
        fields = ['lat', 'long']
        extra_kwargs = {
            'lat': {'required': True},
            'long': {'required': True},
        }


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']


class ProvinceSerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()

    class Meta:
        model = Province
        fields = ['id', 'name', 'country']

    def get_country(self, obj):
        return CountrySerializer(obj.super_region.country).data


class CountySerializer(serializers.ModelSerializer):
    province = serializers.SerializerMethodField()

    class Meta:
        model = County
        fields = ['id', 'name', 'province']

    def get_province(self, obj):
        return ProvinceSerializer(obj.super_region.province).data


class IssueSerializer(serializers.ModelSerializer):
    mission = serializers.PrimaryKeyRelatedField(queryset=Mission.objects.all(), allow_null=True)
    reporter = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = ['id', 'lat', 'long', 'state', 'title', 'description', 'reporter', 'county',
                  'created_at', 'mission', 'image_url']

    def get_reporter(self, obj):
        return UserSerializer(obj.reporter.user).data

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class NestedCountySerializer(serializers.ModelSerializer):
    province = serializers.PrimaryKeyRelatedField(queryset=Province.objects.all(), source='super_region.province')

    class Meta:
        model = County
        fields = ['id', 'name', 'province']


class NestedProvinceSerializer(serializers.ModelSerializer):
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), source='super_region.country')
    sub_regions = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = ['id', 'name', 'country', 'sub_regions']

    def get_sub_regions(self, obj):
        return [NestedCountySerializer(region.county).data for region in obj.sub_regions.all()]


class NestedCountrySerializer(serializers.ModelSerializer):
    sub_regions = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = ['id', 'name', 'sub_regions']

    def get_sub_regions(self, obj):
        return [NestedProvinceSerializer(region.province).data for region in obj.sub_regions.all().order_by('name')]


class IssueReportingSerializer(serializers.ModelSerializer):
    base64_image = serializers.CharField(required=False)

    class Meta:
        model = Issue
        fields = ['lat', 'long', 'title', 'description', 'county', 'base64_image']
        extra_kwargs = {
            'lat': {'required': True},
            'long': {'required': True},
        }


class IssueRatingSerializer(serializers.Serializer):
    rating = serializers.IntegerField(max_value=5, min_value=1, allow_null=True)


class ServicemanSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    team = serializers.PrimaryKeyRelatedField(queryset=ServiceTeam.objects.all())

    class Meta:
        model = Serviceman
        fields = ['lat', 'long', 'user', 'team']

    def get_user(self, obj):
        return UserSerializer(obj.user).data


class ServiceTeamSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()

    class Meta:
        model = ServiceTeam
        fields = ['county', 'active_mission', 'speciality', 'members']

    def get_members(self, obj):
        return ServicemanSerializer(obj.members.all(), many=True).data


class MissionSerializer(serializers.ModelSerializer):
    issue = serializers.SerializerMethodField()
    service_teams = serializers.SerializerMethodField()
    machinery_requirements = serializers.SerializerMethodField()

    class Meta:
        model = Mission
        fields = ['issue', 'service_teams', 'type', 'score', 'report', 'machinery_requirements']

    def get_issue(self, obj):
        return IssueSerializer(obj.issue).data

    def get_service_teams(self, obj):
        return ServiceTeamSerializer(obj.service_teams.all(), many=True).data

    def get_machinery_requirements(self, obj):
        return MachineryRequirementSerializer(obj.issue.machineryrequirement_set.all(), many=True).data


class MissionReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = ['report']
        extra_kwargs = {'report': {'required': True}}


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'password']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone_number': {'validators': []},
        }

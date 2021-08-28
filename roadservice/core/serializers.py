from rest_framework import serializers

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
    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all())

    class Meta:
        model = SpecialityRequirement
        fields = ['id', 'speciality', 'amount', 'issue']


class MachineryRequirementSerializer(serializers.ModelSerializer):
    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all())

    class Meta:
        model = MachineryRequirement
        fields = ['id', 'machinery_type', 'amount', 'issue']


class IssueAcceptanceSerializer(serializers.Serializer):
    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all())
    mission_type = serializers.PrimaryKeyRelatedField(queryset=MissionType.objects.all())
    speciality_requirements = serializers.ListField(child=SpecialityRequirementSerializer(), required=False)
    machinery_requirements = serializers.ListField(child=MachineryRequirementSerializer(), required=False)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serviceman
        fields = ['lat', 'long']


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
    county = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = ['id', 'lat', 'long', 'state', 'title', 'description', 'reporter', 'county',
                  'created_at', 'mission']

    def get_county(self, obj):
        return CountySerializer(obj.county).data


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
        return [NestedProvinceSerializer(region.province).data for region in obj.sub_regions.all()]


class IssueReporingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['lat', 'long', 'title', 'description', 'county']


class IssueRatingSerializer(serializers.Serializer):
    rating = serializers.IntegerField(max_value=5, min_value=1)


class ServicemanSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    team = serializers.PrimaryKeyRelatedField(queryset=ServiceTeam.objects.all())

    class Meta:
        model = Serviceman
        fields = ['lat', 'long', 'user', 'team']

    def get_user(self, obj):
        return UserSerializer(obj.user).data


class ServiceTeamSerializer(serializers.ModelSerializer):
    county = serializers.SerializerMethodField()
    speciality = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = ServiceTeam
        fields = ['county', 'active_mission', 'speciality', 'members']

    def get_members(self, obj):
        return ServicemanSerializer(obj.members.all(), many=True).data

    def get_county(self, obj):
        return CountySerializer(obj.county).data

    def get_speciality(self, obj):
        return SpecialitySerializer(obj.speciality).data


class MissionSerializer(serializers.ModelSerializer):
    issue = serializers.SerializerMethodField()
    service_teams = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    machinery_requirements = serializers.SerializerMethodField()

    class Meta:
        model = Mission
        fields = ['issue', 'service_teams', 'type', 'score', 'report', 'machinery_requirements']

    def get_issue(self, obj):
        return IssueSerializer(obj.issue).data

    def get_service_teams(self, obj):
        return ServiceTeamSerializer(obj.service_teams, many=True).data

    def get_type(self, obj):
        return MissionTypeSerializer(obj.type).data

    def get_machinery_requirements(self, obj):
        return MachineryRequirementSerializer(obj.issue.machineryrequirement_set.all(), many=True).data


class MissionReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = ['report']

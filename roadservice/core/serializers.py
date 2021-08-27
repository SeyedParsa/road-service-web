from rest_framework import serializers

from core.models import Speciality, SpecialityRequirement, Issue, MachineryRequirement, MachineryType, MissionType, \
    Serviceman, Mission, County, Province, Country


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
    speciality_requirements = serializers.ListField(child=SpecialityRequirementSerializer(), required=False)
    machinery_requirements = serializers.ListField(child=MachineryRequirementSerializer(), required=False)


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Serviceman
        fields = ['lat', 'long']


class IssueSerializer(serializers.ModelSerializer):
    mission = serializers.PrimaryKeyRelatedField(queryset=Mission.objects.all(), allow_null=True)
    country_name = serializers.ReadOnlyField(source='county.super_region.province.super_region.country.name')
    province_name = serializers.ReadOnlyField(source='county.super_region.province.name')
    county_name = serializers.ReadOnlyField(source='county.name')

    class Meta:
        model = Issue
        fields = ['id', 'lat', 'long', 'state', 'title', 'description', 'reporter', 'county',
                  'created_at', 'mission', 'county_name', 'province_name', 'country_name']


class CountySerializer(serializers.ModelSerializer):
    province = serializers.PrimaryKeyRelatedField(queryset=Province.objects.all(), source='super_region.province')

    class Meta:
        model = County
        fields = ['id', 'name', 'province']


class ProvinceSerializer(serializers.ModelSerializer):
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), source='super_region.country')
    sub_regions = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = ['id', 'name', 'country', 'sub_regions']

    def get_sub_regions(self, obj):
        return [CountySerializer(region.county).data for region in obj.sub_regions.all()]


class CountrySerializer(serializers.ModelSerializer):
    sub_regions = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = ['id', 'name', 'sub_regions']

    def get_sub_regions(self, obj):
        return [ProvinceSerializer(region.province).data for region in obj.sub_regions.all()]


class IssueReporingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['lat', 'long', 'title', 'description', 'county']


class IssueRatingSerializer(serializers.Serializer):
    rating = serializers.IntegerField(max_value=5, min_value=1)

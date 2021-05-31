from rest_framework import serializers

from core.models import Speciality, SpecialityRequirement, Issue, MachineryRequirement, MachineryType, MissionType


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

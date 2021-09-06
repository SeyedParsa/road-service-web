from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.exceptions import WeakPasswordError
from core.exceptions import AccessDeniedError, IllegalOperationInStateError, InvalidArgumentError, DuplicatedInfoError
from core.models import Location, Issue, Country, Speciality, MachineryType, MissionType, Citizen
from core.permissions import IsCitizen, IsServiceman, IsCountyExpert
from core.serializers import IssueAcceptanceSerializer, LocationSerializer, IssueSerializer, NestedCountrySerializer, \
    IssueReportingSerializer, IssueRatingSerializer, ServiceTeamSerializer, MissionSerializer, MissionReportSerializer, \
    SpecialitySerializer, MachineryTypeSerializer, IssueRejectionSerializer, MissionTypeSerializer, SignUpSerializer


class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']
            phone_number = serializer.validated_data['phone_number']
            password = serializer.validated_data['password']
            try:
                Citizen.sign_up(phone_number, password, phone_number, first_name, last_name)
                return Response({'status': True})
            except (WeakPasswordError, DuplicatedInfoError) as e:
                return Response({'status': False})
        return Response(serializer.errors)


class RegionsListView(APIView):
    def get(self, request):
        country = Country.objects.get()
        return Response(NestedCountrySerializer(country).data)


class SpecialitiesView(APIView):
    def get(self, request):
        specialities = Speciality.objects.all().order_by('name')
        return Response(SpecialitySerializer(specialities, many=True).data)


class MachineryTypesView(APIView):
    def get(self, request):
        machinery_types = MachineryType.objects.all().order_by('name')
        return Response(MachineryTypeSerializer(machinery_types, many=True).data)


class MissionTypesView(APIView):
    def get(self, request):
        mission_types = MissionType.objects.all().order_by('name')
        return Response(MissionTypeSerializer(mission_types, many=True).data)


class CurrentIssueView(APIView):
    permission_classes = [IsAuthenticated, IsCitizen]

    def get(self, request):
        issue_qs = Issue.objects.filter(reporter=request.user.role.citizen).order_by('-created_at')
        if not issue_qs.exists():
            return Response({'state': Issue.State.SCORED.value})
        issue = issue_qs.first()
        return Response(IssueSerializer(issue).data)


class ReportIssueView(APIView):
    permission_classes = [IsAuthenticated, IsCitizen]

    def post(self, request):
        serializer = IssueReportingSerializer(data=request.data)
        if serializer.is_valid():
            lat = serializer.validated_data['lat']
            long = serializer.validated_data['long']
            title = serializer.validated_data['title']
            description = serializer.validated_data['description']
            county = serializer.validated_data['county']
            base64_image = serializer.validated_data.get('base64_image', None)
            citizen = request.user.role.citizen
            try:
                citizen.submit_issue(title=title, description=description, county=county,
                                     location=Location(lat, long), base64_image=base64_image)
                return Response({'status': True})
            except ValidationError as e:
                return Response({'status': False})
        return Response(serializer.errors)


class RateIssueView(APIView):
    permission_classes = [IsAuthenticated, IsCitizen]

    def post(self, request):
        serializer = IssueRatingSerializer(data=request.data)
        if serializer.is_valid():
            rating = serializer.validated_data['rating']
            citizen = request.user.role.citizen
            issue_qs = Issue.objects.filter(reporter=request.user.role.citizen).order_by('-created_at')
            if not issue_qs.exists():
                return Response({'status': False})
            issue = issue_qs.first()
            try:
                citizen.rate_issue(issue, rating)
                return Response({'status': True})
            except (AccessDeniedError, IllegalOperationInStateError) as e:
                return Response({'status': False})
        return Response(serializer.errors)


class ServicemanLocationView(APIView):
    permission_classes = [IsAuthenticated, IsServiceman]

    def get(self, request):
        return Response(LocationSerializer(request.user.role.serviceman).data)


class ServiceTeamView(APIView):
    permission_classes = [IsAuthenticated, IsServiceman]

    def get(self, request):
        return Response(ServiceTeamSerializer(request.user.role.serviceman.team).data)


class CurrentMissionView(APIView):
    permission_classes = [IsAuthenticated, IsServiceman]

    def get(self, request):
        mission = request.user.role.serviceman.team.active_mission
        if not mission:
            return Response({'status': False}, status=404)
        return Response(MissionSerializer(mission).data)


class UpdateLocationView(APIView):
    permission_classes = [IsAuthenticated, IsServiceman]

    def post(self, request, format=None):
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            lat = serializer.validated_data['lat']
            long = serializer.validated_data['long']
            serviceman = request.user.role.serviceman
            serviceman.update_location(Location(lat, long))
            return Response({'status': True})
        return Response(serializer.errors)


class FinishMissionView(APIView):
    permission_classes = [IsAuthenticated, IsServiceman]

    def post(self, request, format=None):
        serializer = MissionReportSerializer(data=request.data)
        if serializer.is_valid():
            report = serializer.validated_data['report']
            serviceman = request.user.role.serviceman
            try:
                serviceman.end_mission(report)
                return Response({'status': True})
            except IllegalOperationInStateError as e:
                return Response({'status': False})
        return Response(serializer.errors)


class ReportedIssuesView(APIView):
    permission_classes = [IsAuthenticated, IsCountyExpert]

    def get(self, request):
        issues = request.user.role.countyexpert.get_reported_issues().order_by('-created_at')
        return Response(IssueSerializer(issues, many=True).data)


class AcceptIssueView(APIView):
    permission_classes = [IsAuthenticated, IsCountyExpert]

    def post(self, request, format=None):
        serializer = IssueAcceptanceSerializer(data=request.data)
        if serializer.is_valid():
            # TODO: test what happens if the request contains invalid foreign keys
            issue = serializer.validated_data['issue']
            mission_type = serializer.validated_data['mission_type']
            speciality_requirements = [tuple(sr.values())
                                       for sr in serializer.validated_data['speciality_requirements']]
            machinery_requirements = [tuple(mr.values())
                                      for mr in serializer.validated_data['machinery_requirements']]
            county_expert = request.user.role.countyexpert
            try:
                county_expert.accept_issue(issue, mission_type, speciality_requirements, machinery_requirements)
                return Response({'status': True})
            except (AccessDeniedError, IllegalOperationInStateError, InvalidArgumentError) as e:
                return Response({'status': False})
        return Response(serializer.errors)


class RejectIssueView(APIView):
    permission_classes = [IsAuthenticated, IsCountyExpert]

    def post(self, request, format=None):
        serializer = IssueRejectionSerializer(data=request.data)
        if serializer.is_valid():
            issue = serializer.validated_data['issue']
            county_expert = request.user.role.countyexpert
            try:
                county_expert.reject_issue(issue)
                return Response({'status': True})
            except IllegalOperationInStateError as e:
                return Response({'status': False})
        return Response(serializer.errors)

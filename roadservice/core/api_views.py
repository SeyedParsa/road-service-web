from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Location, Issue, Country, Speciality, MachineryType
from core.permissions import IsCitizen, IsServiceman, IsCountyExpert
from core.serializers import IssueAcceptanceSerializer, LocationSerializer, IssueSerializer, NestedCountrySerializer, \
    IssueReporingSerializer, IssueRatingSerializer, ServiceTeamSerializer, MissionSerializer, MissionReportSerializer, \
    SpecialitySerializer, MachineryTypeSerializer, IssueRejectionSerializer


class CurrentIssueView(APIView):
    permission_classes = [IsAuthenticated, IsCitizen]

    def get(self, request):
        # TODO: maybe add a get_current_issue to citizen
        issue_qs = Issue.objects.filter(reporter=request.user.role.citizen).order_by('-created_at')
        if not issue_qs.exists():
            return Response({'state': Issue.State.SCORED.value})
        issue = issue_qs.first()
        return Response(IssueSerializer(issue).data)


class RegionsListView(APIView):
    def get(self, request):
        country = Country.objects.get()
        return Response(NestedCountrySerializer(country).data)


class ReportIssueView(APIView):
    permission_classes = [IsAuthenticated, IsCitizen]

    def post(self, request):
        serializer = IssueReporingSerializer(data=request.data)
        if serializer.is_valid():
            lat = serializer.validated_data['lat']
            long = serializer.validated_data['long']
            title = serializer.validated_data['title']
            description = serializer.validated_data['description']
            county = serializer.validated_data['county']
            citizen = request.user.role.citizen
            issue = citizen.submit_issue(title=title, description=description, county=county,
                                         location=Location(lat, long))
            return Response(IssueSerializer(issue).data)
        return Response(serializer.error_messages)  # TODO


class RateIssueView(APIView):
    permission_classes = [IsAuthenticated, IsCitizen]

    def post(self, request):
        serializer = IssueRatingSerializer(data=request.data)
        if serializer.is_valid():
            rating = serializer.validated_data['rating']
            citizen = request.user.role.citizen
            # TODO: use get_currnet_issue
            issue_qs = Issue.objects.filter(reporter=request.user.role.citizen).order_by('-created_at')
            if not issue_qs.exists():
                return Response({'status': False})
            issue = issue_qs.first()
            result = citizen.rate_issue(issue, rating)
            return Response({'status': result})
        return Response(serializer.error_messages)  # TODO


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
            return Response({'status': False})
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
        return Response(serializer.error_messages)  # TODO


class FinishMissionView(APIView):
    permission_classes = [IsAuthenticated, IsServiceman]

    def post(self, request, format=None):
        serializer = MissionReportSerializer(data=request.data)
        if serializer.is_valid():
            report = serializer.validated_data['report']
            serviceman = request.user.role.serviceman
            result = serviceman.end_mission(report)
            return Response({'status': result})
        return Response(serializer.error_messages)  # TODO


class ReportedIssuesView(APIView):
    permission_classes = [IsAuthenticated, IsCountyExpert]

    def get(self, request):
        issues = request.user.role.countyexpert.get_reported_issues().order_by('-created_at')
        return Response(IssueSerializer(issues, many=True).data)


class SpecialitiesView(APIView):
    permission_classes = [IsAuthenticated, IsCountyExpert]

    def get(self, request):
        specialities = Speciality.objects.all()
        return Response(SpecialitySerializer(specialities, many=True).data)


class MachineryTypesView(APIView):
    permission_classes = [IsAuthenticated, IsCountyExpert]

    def get(self, request):
        machinery_types = MachineryType.objects.all()
        return Response(MachineryTypeSerializer(machinery_types, many=True).data)


class AcceptIssueView(APIView):
    permission_classes = [IsAuthenticated, IsCountyExpert]

    def post(self, request, format=None):
        serializer = IssueAcceptanceSerializer(data=request.data)
        if serializer.is_valid():
            issue = serializer.validated_data['issue']
            mission_type = serializer.validated_data['mission_type']
            speciality_requirements = [tuple(sr.values())
                                       for sr in serializer.validated_data['speciality_requirements']]
            machinery_requirements = [tuple(mr.values())
                                      for mr in serializer.validated_data['machinery_requirements']]
            county_expert = request.user.role.countyexpert
            result = county_expert.accept_issue(issue, mission_type, speciality_requirements, machinery_requirements)
            return Response({'status': result})
        print(serializer.__dict__)
        return Response(serializer.error_messages)


class RejectIssueView(APIView):
    permission_classes = [IsAuthenticated, IsCountyExpert]

    def post(self, request, format=None):
        serializer = IssueRejectionSerializer(data=request.data)
        if serializer.is_valid():
            issue = serializer.validated_data['issue']
            county_expert = request.user.role.countyexpert
            result = county_expert.reject_issue(issue)
            return Response({'status': result})
        return Response(serializer.error_messages)

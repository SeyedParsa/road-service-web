from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import CountyExpert, Serviceman, Location, Issue, Country
from core.permissions import IsCitizen, IsServiceman
from core.serializers import IssueAcceptanceSerializer, LocationSerializer, IssueSerializer, NestedCountrySerializer, \
    IssueReporingSerializer, IssueRatingSerializer, ServiceTeamSerializer, MissionSerializer, MissionReportSerializer


class AcceptIssueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = IssueAcceptanceSerializer(data=request.data)
        if serializer.is_valid():
            issue = serializer.validated_data['issue']
            mission_type = serializer.validated_data['mission_type']
            speciality_requirements = [tuple(sr.values())
                                       for sr in serializer.validated_data['speciality_requirements']]
            machinery_requirements = [tuple(mr.values())
                                      for mr in serializer.validated_data['machinery_requirements']]
            # TODO: select the corresponding county expert (this is for EAB)
            county_expert = CountyExpert.objects.all()[0]
            result = county_expert.accept_issue(issue, mission_type, speciality_requirements, machinery_requirements)
            return Response(result)
        return Response(serializer.error_messages)


class CurrentIssueView(APIView):
    permission_classes = [IsAuthenticated, IsCitizen]

    def get(self, request):
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
            county = serializer.validated_data['county']
            pass  # TODO: backend + error
            issue = Issue.objects.first()
            return Response(IssueSerializer(issue).data)
        return Response(serializer.error_messages)  # TODO


class RateIssueView(APIView):
    permission_classes = [IsAuthenticated, IsCitizen]

    def post(self, request):
        serializer = IssueRatingSerializer(data=request.data)
        if serializer.is_valid():
            rating = serializer.validated_data['rating']
            pass  # TODO: backend + error
            return Response({'status': True})
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
            pass  # TODO: backend
            return Response({'status': True})
        return Response(serializer.error_messages)  # TODO


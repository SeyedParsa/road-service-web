from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import CountyExpert, Serviceman, Location, Issue, Country
from core.permissions import IsCitizen
from core.serializers import IssueAcceptanceSerializer, LocationSerializer, IssueSerializer, CountrySerializer, \
    IssueReporingSerializer, IssueRatingSerializer


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


class UpdateLocationView(APIView):
    def post(self, request, format=None):
        # TODO: select the corresponding serviceman (this is for EAB)
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            lat = serializer.validated_data['lat']
            long = serializer.validated_data['long']
            service_man = Serviceman.objects.all()[0]
            service_man.update_location(Location(lat, long))
            return Response("Updated!")
        return Response(serializer.error_messages)


class CurrentIssueView(APIView):
    permission_classes = [IsAuthenticated, IsCitizen]

    def get(self, request):
        issue_qs = Issue.objects.filter(reporter=request.user.role.citizen).order_by('-created_at')
        if not issue_qs.exists():
            return Response(None)
        issue = issue_qs.first()
        return Response(IssueSerializer(issue).data)


class RegionsListView(APIView):
    def get(self, request):
        country = Country.objects.get()
        return Response(CountrySerializer(country).data)


class ReportIssueView(APIView):
    def post(self, request):
        serializer = IssueReporingSerializer(data=request.data)
        if serializer.is_valid():
            county = serializer.validated_data['county']
            pass  # TODO: backend + error
            issue = Issue.objects.get()
            return Response(IssueSerializer(issue).data)
        return Response(serializer.error_messages)


class RateIssueView(APIView):
    def post(self, request):
        serializer = IssueRatingSerializer(data=request.data)
        if serializer.is_valid():
            rating = serializer.validated_data['rating']
            pass  # TODO: backend + error
            return Response({'status': True})
        return Response(serializer.error_messages)

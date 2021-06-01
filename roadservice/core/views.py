from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import CountyExpert, Serviceman, Location
from core.serializers import IssueAcceptanceSerializer, LocationSerializer


class AcceptIssue(APIView):
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


class UpdateLocation(APIView):
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

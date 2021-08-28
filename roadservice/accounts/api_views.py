from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import UserSerializer, SignUpSerializer


class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            pass  # TODO
            return Response({'error': 'PHONE_DUPLICATE'})
        return Response({'status': False})

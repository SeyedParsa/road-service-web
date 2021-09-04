from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.exceptions import WeakPasswordError
from accounts.serializers import UserSerializer, PasswordSerializer


class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data['password']
            try:
                request.user.change_password(password)
                return Response({'status': True})
            except WeakPasswordError as e:
                return Response({'status': False})
        return Response(serializer.errors)

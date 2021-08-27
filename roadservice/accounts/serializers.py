from rest_framework import serializers

from accounts.models import User, Role


class UserSerializer(serializers.ModelSerializer):
    role = serializers.ReadOnlyField(source='role.type')

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'phone_number', 'role']


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']

from typing import Any

from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile data (used by admin endpoints)."""

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role',
            'first_name', 'last_name', 'bio',
            'date_joined',
        ]
        read_only_fields = ['id', 'date_joined']


class CurrentUserSerializer(UserSerializer):
    """Serializer for the self-service /api/auth/me/ endpoint.

    Locks `role`, `username`, and `email` as read-only so an authenticated
    user cannot escalate their own privileges or impersonate another account
    via PATCH. Role changes must go through the admin user management API.
    """

    class Meta(UserSerializer.Meta):
        read_only_fields = UserSerializer.Meta.read_only_fields + [
            'role', 'username', 'email',
        ]


class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration with validation."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=[('student', 'Student'), ('teacher', 'Teacher')])

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return data

    def create(self, validated_data: dict[str, Any]) -> User:
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login with credential validation."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Invalid username or password.")
        data['user'] = user
        return data

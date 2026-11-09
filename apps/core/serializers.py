"""Serializers for the core app."""

from rest_framework import serializers


class CoreLoginSerializer(serializers.Serializer):
    """Validate the login payload."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class CoreLoginResponseSerializer(serializers.Serializer):
    """Format the login response."""

    token = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)


class CoreUserInfoSerializer(serializers.Serializer):
    """Format the authenticated user data."""

    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)


class CoreChangePasswordSerializer(serializers.Serializer):
    """Validate the password change payload."""

    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)


class CoreChangeNameSerializer(serializers.Serializer):
    """Validate the name change payload."""

    first_name = serializers.CharField()
    last_name = serializers.CharField()

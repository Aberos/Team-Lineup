from rest_framework import serializers


class CoreLoginSerializer(serializers.Serializer):
    """Serializer for the core login view."""

    username = serializers.CharField()
    password = serializers.CharField()


class CoreLoginResponseSerializer(serializers.Serializer):
    """Serializer for the core login response."""

    token = serializers.CharField()


class CoreUserInfoSerializer(serializers.Serializer):
    """Serializer for the authenticated user info view."""

    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()


class CoreChangePasswordSerializer(serializers.Serializer):
    """Serializer for the authenticated user password change view."""

    current_password = serializers.CharField()
    new_password = serializers.CharField()


class CoreChangeNameSerializer(serializers.Serializer):
    """Serializer for the authenticated user name change view."""

    first_name = serializers.CharField()
    last_name = serializers.CharField()

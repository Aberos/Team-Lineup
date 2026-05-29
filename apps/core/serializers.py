from rest_framework import serializers


class CoreLoginSerializer(serializers.Serializer):
    """Serializer for the core login view."""

    username = serializers.CharField()
    password = serializers.CharField()

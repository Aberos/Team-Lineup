from rest_framework import serializers


class RoleCreateSerializer(serializers.Serializer):
    """Serializer for creating a new role."""

    name = serializers.CharField(max_length=100)


class RoleListSerializer(serializers.Serializer):
    """Serializer for listing roles."""

    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)


class RoleDetailSerializer(serializers.Serializer):
    """Serializer for retrieving a specific role."""

    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)


class RoleUpdateSerializer(serializers.Serializer):
    """Serializer for updating a specific role."""

    name = serializers.CharField(max_length=100)

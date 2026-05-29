"""DRF API views for the core app."""

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers import CoreLoginSerializer
from apps.core.service import CoreService


@extend_schema(
    request=CoreLoginSerializer,
    responses={200: CoreLoginSerializer},
)
class CoreLoginView(APIView):
    """Core API view."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = CoreLoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        result = CoreService.login(username=username, password=password)

        if result is None:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        return Response({"token": result["token"]}, status=status.HTTP_200_OK)

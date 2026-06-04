"""DRF API views for the core app."""

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.serializers import (
    CoreChangeNameSerializer,
    CoreChangePasswordSerializer,
    CoreLoginResponseSerializer,
    CoreLoginSerializer,
    CoreUserInfoSerializer,
)
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

        serializer = CoreLoginResponseSerializer(data=result)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(description="Validate a token.", responses={200: None})
class CoreValidateTokenView(APIView):
    """Core API view for validating tokens."""

    def _extract_token_from_header(self, auth_header: str) -> str:
        """Extract token from Authorization header."""
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        return auth_header

    def get(self, request: Request) -> Response:
        auth_header = request.headers.get("Authorization")
        token = self._extract_token_from_header(auth_header)

        if auth_header is None or token is None:
            return Response(None, status=status.HTTP_401_UNAUTHORIZED)

        is_valid = CoreService.validate_token(token)
        if not is_valid:
            return Response(None, status=status.HTTP_401_UNAUTHORIZED)

        return Response(None, status=status.HTTP_200_OK)


@extend_schema(
    description="Get user authenticated info.",
    responses={200: CoreUserInfoSerializer},
)
class CoreAuthenticatedUserInfoView(APIView):
    """Core API view for getting user authenticated info."""

    def get(self, request: Request) -> Response:
        serializer = CoreUserInfoSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    description="Change user authenticated password.",
    request=CoreChangePasswordSerializer,
    responses={200: None},
)
class CoreAuthenticatedUserChangePasswordView(APIView):
    """Core API view for change user authenticated password."""

    def patch(self, request: Request) -> Response:
        serializer = CoreChangePasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        password_changed = CoreService.change_password(
            user=request.user,
            current_password=serializer.validated_data["current_password"],
            new_password=serializer.validated_data["new_password"],
        )

        if not password_changed:
            return Response(None, status=status.HTTP_401_UNAUTHORIZED)

        return Response(None, status=status.HTTP_200_OK)


@extend_schema(
    description="Change user authenticated name.",
    request=CoreChangeNameSerializer,
    responses={200: None},
)
class CoreAuthenticatedUserChangeNameView(APIView):
    """Core API view for change user authenticated name."""

    def patch(self, request: Request) -> Response:
        serializer = CoreChangeNameSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        CoreService.change_name(
            user=request.user,
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"],
        )

        return Response(None, status=status.HTTP_200_OK)

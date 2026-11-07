"""DRF API views for the core app."""

from typing import cast

from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import InvalidCredentialsError
from apps.core.serializers import (
    CoreChangeNameSerializer,
    CoreChangePasswordSerializer,
    CoreLoginResponseSerializer,
    CoreLoginSerializer,
    CoreUserInfoSerializer,
)
from apps.core.service import CoreService

_AUTH_TAG = "auth"


class CoreLoginView(APIView):
    """Authenticate a user and issue a JWT access token."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=[_AUTH_TAG],
        description="Authenticate with username and password.",
        request=CoreLoginSerializer,
        responses={200: CoreLoginResponseSerializer, 400: None},
    )
    def post(self, request: Request) -> Response:
        """Return an access token for valid credentials."""
        serializer = CoreLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token = CoreService.login(
                username=serializer.validated_data["username"],
                password=serializer.validated_data["password"],
            )
        except InvalidCredentialsError:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            CoreLoginResponseSerializer({"token": token}).data,
            status=status.HTTP_200_OK,
        )


class CoreValidateTokenView(APIView):
    """Check whether the bearer token is valid."""

    @extend_schema(
        tags=[_AUTH_TAG],
        description="Validate the access token sent in the header.",
        responses={200: None, 401: None},
    )
    def get(self, request: Request) -> Response:
        """Return 200 when the JWT authentication succeeds."""
        return Response(status=status.HTTP_200_OK)


class CoreAuthenticatedUserInfoView(APIView):
    """Expose the data of the authenticated user."""

    @extend_schema(
        tags=[_AUTH_TAG],
        description="Retrieve the authenticated user data.",
        responses={200: CoreUserInfoSerializer, 401: None},
    )
    def get(self, request: Request) -> Response:
        """Return the authenticated user data."""
        return Response(
            CoreUserInfoSerializer(request.user).data,
            status=status.HTTP_200_OK,
        )


class CoreAuthenticatedUserChangePasswordView(APIView):
    """Change the password of the authenticated user."""

    @extend_schema(
        tags=[_AUTH_TAG],
        description="Change the authenticated user password.",
        request=CoreChangePasswordSerializer,
        responses={204: None, 400: None, 401: None},
    )
    def patch(self, request: Request) -> Response:
        """Replace the password after checking the current one."""
        serializer = CoreChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            CoreService.change_password(
                user=cast(User, request.user),
                current_password=serializer.validated_data["current_password"],
                new_password=serializer.validated_data["new_password"],
            )
        except InvalidCredentialsError:
            return Response(
                {"current_password": ["Current password is incorrect."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class CoreAuthenticatedUserChangeNameView(APIView):
    """Change the name of the authenticated user."""

    @extend_schema(
        tags=[_AUTH_TAG],
        description="Change the authenticated user first and last names.",
        request=CoreChangeNameSerializer,
        responses={200: CoreUserInfoSerializer, 400: None, 401: None},
    )
    def patch(self, request: Request) -> Response:
        """Update the names and return the user data."""
        serializer = CoreChangeNameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CoreService.change_name(
            user=cast(User, request.user),
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"],
        )
        return Response(
            CoreUserInfoSerializer(user).data, status=status.HTTP_200_OK
        )

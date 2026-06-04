"""Core API tests."""

import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework_simplejwt.tokens import AccessToken

_BASE = "/api/v1"


class CoreLoginView(TestCase):
    """Tests for the core login view."""

    def setUp(self):
        self.client = Client()

    def test_login_success(self) -> None:
        """Test successful login."""
        get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )

        request_body = {"username": "testuser", "password": "testpass"}
        response = self.client.post(
            f"{_BASE}/auth/login/",
            json.dumps(request_body),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_login_without_data_returns_400(self) -> None:
        """Test login without data returns 400."""
        response = self.client.post(
            f"{_BASE}/auth/login/", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_login_required_fields(self) -> None:
        """Test login with missing required fields returns 400."""
        request_body = {"username": "testuser"}
        response = self.client.post(
            f"{_BASE}/auth/login/",
            json.dumps(request_body),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_login_invalid_credentials(self) -> None:
        """Test login with invalid credentials returns 400."""
        request_body = {"username": "testuser", "password": "wrongpass"}
        response = self.client.post(
            f"{_BASE}/auth/login/",
            json.dumps(request_body),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_login_returns_token(self) -> None:
        """Test login with valid credentials returns token."""
        get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )

        request_body = {"username": "testuser", "password": "testpass"}
        response = self.client.post(
            f"{_BASE}/auth/login/",
            json.dumps(request_body),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json())

    def test_login_inactive_user(self) -> None:
        """Test login with inactive user returns 400."""
        get_user_model().objects.create_user(
            username="testuser", password="testpass", is_active=False
        )

        request_body = {"username": "testuser", "password": "testpass"}
        response = self.client.post(
            f"{_BASE}/auth/login/",
            json.dumps(request_body),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


class CoreValidateTokenView(TestCase):
    """Tests for the core validate token view."""

    def setUp(self) -> None:
        self.client = Client()

    def test_validate_token_returns_success(self) -> None:
        """Test successful token validation."""
        get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )

        request_body = {"username": "testuser", "password": "testpass"}
        response = self.client.post(
            f"{_BASE}/auth/login/",
            json.dumps(request_body),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        token = response.json().get("token")

        response = self.client.get(
            f"{_BASE}/auth/validate-token/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_validate_token_returns_401_for_invalid_token(self) -> None:
        """Test token validation with invalid token returns 401."""
        response = self.client.get(
            f"{_BASE}/auth/validate-token/",
            HTTP_AUTHORIZATION="Bearer invalidtoken",
        )
        self.assertEqual(response.status_code, 401)

    def test_validate_token_returns_401_for_missing_token(self) -> None:
        """Test token validation with missing token returns 401."""
        response = self.client.get(f"{_BASE}/auth/validate-token/")
        self.assertEqual(response.status_code, 401)

    def test_validate_token_returns_401_for_expired_token(self) -> None:
        """Test token validation with expired token returns 401."""
        user = get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )

        expired_token = AccessToken.for_user(user)
        expired_token.set_exp(lifetime=timedelta(seconds=-1))

        response = self.client.get(
            f"{_BASE}/auth/validate-token/",
            HTTP_AUTHORIZATION=f"Bearer {expired_token}",
        )
        self.assertEqual(response.status_code, 401)


class CoreAuthenticatedUserInfoView(TestCase):
    """Tests for a view that requires authentication."""

    def setUp(self) -> None:
        self.client = Client()

    def test_authenticated_user_info_returns_success(self) -> None:
        """Test authenticated request to me view returns success."""
        get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            first_name="John",
            last_name="Doe",
            email="testuser@example.com",
        )

        request_body = {"username": "testuser", "password": "testpass"}
        response = self.client.post(
            f"{_BASE}/auth/login/",
            json.dumps(request_body),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        token = response.json().get("token")

        response = self.client.get(
            f"{_BASE}/auth/me/", HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "username": "testuser",
                "first_name": "John",
                "last_name": "Doe",
                "email": "testuser@example.com",
            },
        )

    def test_unauthenticated_user_returns_401(self) -> None:
        """Test unauthenticated request to me view returns 401."""
        response = self.client.get(f"{_BASE}/auth/me/")
        self.assertEqual(response.status_code, 401)

    def test_user_with_invalid_token_returns_401(self) -> None:
        """Test request to me view with invalid token returns 401."""
        response = self.client.get(
            f"{_BASE}/auth/me/", HTTP_AUTHORIZATION="Bearer invalidtoken"
        )

        self.assertEqual(response.status_code, 401)

    def test_user_with_expired_token_returns_401(self) -> None:
        """Test request to me view with expired token returns 401."""
        user = get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )

        expired_token = AccessToken.for_user(user)
        expired_token.set_exp(lifetime=timedelta(seconds=-1))

        response = self.client.get(
            f"{_BASE}/auth/me/", HTTP_AUTHORIZATION=f"Bearer {expired_token}"
        )
        self.assertEqual(response.status_code, 401)


class CoreAuthenticatedUserChangePasswordView(TestCase):
    """Tests for the core authenticated user change password view."""

    def setUp(self) -> None:
        self.client = Client()

    def test_change_password_success(self) -> None:
        """Test successful change user authenticated password."""
        get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )

        request_login_body = {"username": "testuser", "password": "testpass"}
        response_login = self.client.post(
            f"{_BASE}/auth/login/",
            json.dumps(request_login_body),
            content_type="application/json",
        )

        self.assertEqual(response_login.status_code, 200)
        token = response_login.json().get("token")

        request_change_password_body = {
            "current_password": "testpass",
            "new_password": "456",
        }
        response_change_password = self.client.patch(
            f"{_BASE}/auth/change-password",
            json.dumps(request_change_password_body),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response_change_password.status_code, 200)

        request_login_body = {"username": "testuser", "password": "456"}
        response_login = self.client.post(
            f"{_BASE}/auth/login/",
            json.dumps(request_login_body),
            content_type="application/json",
        )

        self.assertEqual(response_login.status_code, 200)

    def test_change_password_unauthenticated_returns_401(self) -> None:
        """Test unauthenticated change password request returns 401."""
        request_change_password_body = {
            "current_password": "testpass",
            "new_password": "456",
        }
        response_change_password = self.client.patch(
            f"{_BASE}/auth/change-password",
            json.dumps(request_change_password_body),
            content_type="application/json",
        )

        self.assertEqual(response_change_password.status_code, 401)

    def test_change_password_invalid_current_returns_401(self) -> None:
        """Test change password with invalid current password returns 401."""
        get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )

        request_login_body = {"username": "testuser", "password": "testpass"}
        response_login = self.client.post(
            f"{_BASE}/auth/login/",
            json.dumps(request_login_body),
            content_type="application/json",
        )

        self.assertEqual(response_login.status_code, 200)
        token = response_login.json().get("token")

        request_change_password_body = {
            "current_password": "wrongpass",
            "new_password": "456",
        }
        response_change_password = self.client.patch(
            f"{_BASE}/auth/change-password",
            json.dumps(request_change_password_body),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response_change_password.status_code, 401)

    def test_change_password_empty_fields_returns_400(self) -> None:
        """Test change password with empty password fields returns 400."""
        get_user_model().objects.create_user(
            username="testuser", password="testpass"
        )

        request_login_body = {"username": "testuser", "password": "testpass"}
        response_login = self.client.post(
            f"{_BASE}/auth/login/",
            json.dumps(request_login_body),
            content_type="application/json",
        )

        self.assertEqual(response_login.status_code, 200)
        token = response_login.json().get("token")

        request_bodies = [
            {"current_password": "", "new_password": "456"},
            {"current_password": "testpass", "new_password": ""},
        ]

        for request_body in request_bodies:
            with self.subTest(request_body=request_body):
                response_change_password = self.client.patch(
                    f"{_BASE}/auth/change-password",
                    json.dumps(request_body),
                    content_type="application/json",
                    HTTP_AUTHORIZATION=f"Bearer {token}",
                )

                self.assertEqual(response_change_password.status_code, 400)


class CoreAuthenticatedUserChangeNameView(TestCase):
    """Tests for the core authenticated user change name view."""

    def setUp(self) -> None:
        self.client = Client()

    def test_change_name_success(self) -> None:
        """Test successful change user authenticated name."""
        user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            first_name="John",
            last_name="Doe",
        )

        request_login_body = {"username": "testuser", "password": "testpass"}
        response_login = self.client.post(
            f"{_BASE}/auth/login/",
            json.dumps(request_login_body),
            content_type="application/json",
        )

        self.assertEqual(response_login.status_code, 200)
        token = response_login.json().get("token")

        request_change_name_body = {
            "first_name": "Michael",
            "last_name": "Doe",
        }
        response_change_name = self.client.patch(
            f"{_BASE}/auth/change-name",
            json.dumps(request_change_name_body),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        self.assertEqual(response_change_name.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Michael")
        self.assertEqual(user.last_name, "Doe")

    def test_change_name_unauthenticated_returns_401(self) -> None:
        """Test unauthenticated change name request returns 401."""
        request_change_name_body = {
            "first_name": "Michael",
            "last_name": "Doe",
        }
        response_change_name = self.client.patch(
            f"{_BASE}/auth/change-name",
            json.dumps(request_change_name_body),
            content_type="application/json",
        )

        self.assertEqual(response_change_name.status_code, 401)

    def test_change_name_empty_fields_returns_400(self) -> None:
        """Test change name with empty name fields returns 400."""
        get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            first_name="John",
            last_name="Doe",
        )

        request_login_body = {"username": "testuser", "password": "testpass"}
        response_login = self.client.post(
            f"{_BASE}/auth/login/",
            json.dumps(request_login_body),
            content_type="application/json",
        )

        self.assertEqual(response_login.status_code, 200)
        token = response_login.json().get("token")

        request_bodies = [
            {"first_name": "", "last_name": "Doe"},
            {"first_name": "Michael", "last_name": ""},
        ]

        for request_body in request_bodies:
            with self.subTest(request_body=request_body):
                response_change_name = self.client.patch(
                    f"{_BASE}/auth/change-name",
                    json.dumps(request_body),
                    content_type="application/json",
                    HTTP_AUTHORIZATION=f"Bearer {token}",
                )

                self.assertEqual(response_change_name.status_code, 400)

    def test_change_name_missing_fields_returns_400(self) -> None:
        """Test change name with missing name fields returns 400."""
        get_user_model().objects.create_user(
            username="testuser",
            password="testpass",
            first_name="John",
            last_name="Doe",
        )

        request_login_body = {"username": "testuser", "password": "testpass"}
        response_login = self.client.post(
            f"{_BASE}/auth/login/",
            json.dumps(request_login_body),
            content_type="application/json",
        )

        self.assertEqual(response_login.status_code, 200)
        token = response_login.json().get("token")

        request_bodies = [
            {"first_name": "Michael"},
            {"last_name": "Doe"},
        ]

        for request_body in request_bodies:
            with self.subTest(request_body=request_body):
                response_change_name = self.client.patch(
                    f"{_BASE}/auth/change-name",
                    json.dumps(request_body),
                    content_type="application/json",
                    HTTP_AUTHORIZATION=f"Bearer {token}",
                )

                self.assertEqual(response_change_name.status_code, 400)

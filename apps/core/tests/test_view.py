"""Core API tests."""

import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

_BASE = "/api/v1"


class CoreLoginView(TestCase):
    """Tests for the core login view."""

    def setUp(self):
        self.client = Client()

    def test_login_success(self) -> None:
        """Test successful login."""
        get_user_model().objects.create_user(username="testuser", password="testpass")

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
        get_user_model().objects.create_user(username="testuser", password="testpass")

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

"""Tests for the players API views."""

import json
from datetime import date

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, TestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.players.models import Player, PlayerRole, Role

_BASE = "/api/v1/role"
_MISSING_ID = 999_999


class RoleListCreateViewTests(TestCase):
    """Tests for the role list and create endpoint."""

    def setUp(self) -> None:
        self.client = Client()
        user = get_user_model().objects.create_user(
            username="tester", password="secret-pass"
        )
        self.auth = {
            "HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(user)}"
        }

    def test_list_roles_returns_200_ordered_by_name(self) -> None:
        """List every role ordered by name."""
        Role.objects.create(name="Striker")
        Role.objects.create(name="Goalkeeper")

        response = self.client.get(f"{_BASE}/", **self.auth)

        self.assertEqual(response.status_code, 200)
        names = [role["name"] for role in response.json()]
        self.assertEqual(names, ["Goalkeeper", "Striker"])

    def test_list_roles_without_token_returns_401(self) -> None:
        """Reject listing without authentication."""
        response = self.client.get(f"{_BASE}/")

        self.assertEqual(response.status_code, 401)

    def test_create_role_returns_201_with_body(self) -> None:
        """Create a role and return its data."""
        response = self.client.post(
            f"{_BASE}/",
            json.dumps({"name": "Goalkeeper"}),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 201)
        role = Role.objects.get(name="Goalkeeper")
        self.assertEqual(
            response.json(), {"id": role.id, "name": "Goalkeeper"}
        )

    def test_create_role_without_name_returns_400(self) -> None:
        """Reject role creation without a name."""
        response = self.client.post(
            f"{_BASE}/",
            json.dumps({}),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("name", response.json())

    def test_create_role_without_token_returns_401(self) -> None:
        """Reject role creation without authentication."""
        response = self.client.post(
            f"{_BASE}/",
            json.dumps({"name": "Goalkeeper"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)


class RoleDetailViewTests(TestCase):
    """Tests for the role detail endpoint."""

    def setUp(self) -> None:
        self.client = Client()
        user = get_user_model().objects.create_user(
            username="tester", password="secret-pass"
        )
        self.auth = {
            "HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(user)}"
        }
        self.role = Role.objects.create(name="Goalkeeper")

    def test_get_role_returns_200(self) -> None:
        """Return the requested role."""
        response = self.client.get(f"{_BASE}/{self.role.id}/", **self.auth)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"id": self.role.id, "name": "Goalkeeper"}
        )

    def test_get_missing_role_returns_404(self) -> None:
        """Return 404 for an unknown role."""
        response = self.client.get(f"{_BASE}/{_MISSING_ID}/", **self.auth)

        self.assertEqual(response.status_code, 404)

    def test_get_role_without_token_returns_401(self) -> None:
        """Reject retrieval without authentication."""
        response = self.client.get(f"{_BASE}/{self.role.id}/")

        self.assertEqual(response.status_code, 401)

    def test_update_role_returns_200(self) -> None:
        """Rename the requested role."""
        response = self.client.put(
            f"{_BASE}/{self.role.id}/",
            json.dumps({"name": "Defender"}),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200)
        self.role.refresh_from_db()
        self.assertEqual(self.role.name, "Defender")

    def test_update_role_without_name_returns_400(self) -> None:
        """Reject an update without a name."""
        response = self.client.put(
            f"{_BASE}/{self.role.id}/",
            json.dumps({}),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 400)

    def test_update_missing_role_returns_404(self) -> None:
        """Return 404 when updating an unknown role."""
        response = self.client.put(
            f"{_BASE}/{_MISSING_ID}/",
            json.dumps({"name": "Defender"}),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 404)

    def test_update_role_without_token_returns_401(self) -> None:
        """Reject an update without authentication."""
        response = self.client.put(
            f"{_BASE}/{self.role.id}/",
            json.dumps({"name": "Defender"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

    def test_delete_role_returns_204(self) -> None:
        """Delete the requested role."""
        response = self.client.delete(f"{_BASE}/{self.role.id}/", **self.auth)

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Role.objects.filter(id=self.role.id).exists())

    def test_delete_missing_role_returns_404(self) -> None:
        """Return 404 when deleting an unknown role."""
        response = self.client.delete(f"{_BASE}/{_MISSING_ID}/", **self.auth)

        self.assertEqual(response.status_code, 404)

    def test_delete_role_without_token_returns_401(self) -> None:
        """Reject deletion without authentication."""
        response = self.client.delete(f"{_BASE}/{self.role.id}/")

        self.assertEqual(response.status_code, 401)


_PLAYER_BASE = "/api/v1/player"
_PLAYER_PAYLOAD = {
    "name": "Ana Souza",
    "birthday": "1995-04-10",
    "phone": "11999990000",
    "email": "ana@example.com",
    "number": 10,
}


class PlayerViewTests(TestCase):
    """Tests for the player endpoints."""

    def setUp(self) -> None:
        self.client = Client()
        user = get_user_model().objects.create_user(
            username="tester", password="secret-pass"
        )
        self.auth = {
            "HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(user)}"
        }

    def _create_player(self, **overrides: object) -> Player:
        """Persist a player with default data."""
        data = {
            "name": "Bruno Lima",
            "birthday": date(1990, 1, 1),
            "phone": "11888880000",
            "email": "bruno@example.com",
            "number": 7,
        }
        data.update(overrides)
        return Player.objects.create(**data)

    def _send(self, method: str, url: str, body: object) -> HttpResponse:
        """Send a JSON request with authentication."""
        return getattr(self.client, method)(
            url,
            json.dumps(body),
            content_type="application/json",
            **self.auth,
        )

    def test_list_players_returns_200(self) -> None:
        """List every player ordered by name."""
        self._create_player(name="Carla", email="carla@example.com")
        self._create_player(name="Bruno")

        response = self.client.get(f"{_PLAYER_BASE}/", **self.auth)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [player["name"] for player in response.json()],
            ["Bruno", "Carla"],
        )

    def test_list_players_without_token_returns_401(self) -> None:
        """Reject listing without authentication."""
        response = self.client.get(f"{_PLAYER_BASE}/")

        self.assertEqual(response.status_code, 401)

    def test_create_player_returns_201(self) -> None:
        """Create a player and return its data."""
        response = self._send("post", f"{_PLAYER_BASE}/", _PLAYER_PAYLOAD)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], "ana@example.com")
        self.assertTrue(Player.objects.filter(name="Ana Souza").exists())

    def test_create_player_invalid_data_returns_400(self) -> None:
        """Reject invalid email, negative number and future birthday."""
        invalid_payloads = [
            {**_PLAYER_PAYLOAD, "email": "invalid"},
            {**_PLAYER_PAYLOAD, "number": -1},
            {**_PLAYER_PAYLOAD, "birthday": "2999-01-01"},
            {},
        ]

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self._send("post", f"{_PLAYER_BASE}/", payload)
                self.assertEqual(response.status_code, 400)

    def test_create_player_duplicated_email_returns_409(self) -> None:
        """Reject a second player with the same email."""
        self._create_player(email="ana@example.com")

        response = self._send(
            "post",
            f"{_PLAYER_BASE}/",
            {**_PLAYER_PAYLOAD, "email": "ANA@example.com"},
        )

        self.assertEqual(response.status_code, 409)

    def test_create_player_without_token_returns_401(self) -> None:
        """Reject creation without authentication."""
        response = self.client.post(
            f"{_PLAYER_BASE}/",
            json.dumps(_PLAYER_PAYLOAD),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

    def test_get_player_returns_200(self) -> None:
        """Return the requested player."""
        player = self._create_player()

        response = self.client.get(f"{_PLAYER_BASE}/{player.id}/", **self.auth)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["birthday"], "1990-01-01")

    def test_get_missing_player_returns_404(self) -> None:
        """Return 404 for an unknown player."""
        response = self.client.get(
            f"{_PLAYER_BASE}/{_MISSING_ID}/", **self.auth
        )

        self.assertEqual(response.status_code, 404)

    def test_update_player_returns_200(self) -> None:
        """Replace the data of a player."""
        player = self._create_player()

        response = self._send(
            "put", f"{_PLAYER_BASE}/{player.id}/", _PLAYER_PAYLOAD
        )

        self.assertEqual(response.status_code, 200)
        player.refresh_from_db()
        self.assertEqual(player.name, "Ana Souza")

    def test_update_player_invalid_data_returns_400(self) -> None:
        """Reject an update with missing fields."""
        player = self._create_player()

        response = self._send(
            "put", f"{_PLAYER_BASE}/{player.id}/", {"name": "X"}
        )

        self.assertEqual(response.status_code, 400)

    def test_update_player_email_of_other_returns_409(self) -> None:
        """Reject an update that reuses the email of another player."""
        self._create_player(email="ana@example.com")
        player = self._create_player(email="other@example.com")

        response = self._send(
            "put", f"{_PLAYER_BASE}/{player.id}/", _PLAYER_PAYLOAD
        )

        self.assertEqual(response.status_code, 409)

    def test_update_missing_player_returns_404(self) -> None:
        """Return 404 when updating an unknown player."""
        response = self._send(
            "put", f"{_PLAYER_BASE}/{_MISSING_ID}/", _PLAYER_PAYLOAD
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_player_returns_204(self) -> None:
        """Delete the requested player."""
        player = self._create_player()

        response = self.client.delete(
            f"{_PLAYER_BASE}/{player.id}/", **self.auth
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Player.objects.filter(id=player.id).exists())

    def test_delete_missing_player_returns_404(self) -> None:
        """Return 404 when deleting an unknown player."""
        response = self.client.delete(
            f"{_PLAYER_BASE}/{_MISSING_ID}/", **self.auth
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_player_without_token_returns_401(self) -> None:
        """Reject deletion without authentication."""
        player = self._create_player()

        response = self.client.delete(f"{_PLAYER_BASE}/{player.id}/")

        self.assertEqual(response.status_code, 401)


class PlayerRoleViewTests(TestCase):
    """Tests for the player role assignment endpoints."""

    def setUp(self) -> None:
        self.client = Client()
        user = get_user_model().objects.create_user(
            username="tester", password="secret-pass"
        )
        self.auth = {
            "HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(user)}"
        }
        self.player = Player.objects.create(
            name="Ana",
            birthday=date(1995, 4, 10),
            phone="11999990000",
            email="ana@example.com",
            number=10,
        )
        self.role = Role.objects.create(name="Goalkeeper")
        self.url = f"{_PLAYER_BASE}/{self.player.id}/role/"

    def _assign(self, role_id: int, player_url: str = "") -> HttpResponse:
        """Send an authenticated role assignment request."""
        return self.client.post(
            player_url or self.url,
            json.dumps({"role_id": role_id}),
            content_type="application/json",
            **self.auth,
        )

    def test_list_player_roles_returns_200(self) -> None:
        """List the roles assigned to the player."""
        PlayerRole.objects.create(player=self.player, role=self.role)

        response = self.client.get(self.url, **self.auth)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), [{"id": self.role.id, "name": "Goalkeeper"}]
        )

    def test_list_roles_of_missing_player_returns_404(self) -> None:
        """Return 404 for an unknown player."""
        response = self.client.get(
            f"{_PLAYER_BASE}/{_MISSING_ID}/role/", **self.auth
        )

        self.assertEqual(response.status_code, 404)

    def test_list_player_roles_without_token_returns_401(self) -> None:
        """Reject listing without authentication."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_assign_role_returns_201(self) -> None:
        """Assign a role to the player."""
        response = self._assign(self.role.id)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            PlayerRole.objects.filter(
                player=self.player, role=self.role
            ).exists()
        )

    def test_assign_role_without_role_id_returns_400(self) -> None:
        """Reject an assignment without role identifier."""
        response = self.client.post(
            self.url,
            json.dumps({}),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 400)

    def test_assign_missing_role_returns_400(self) -> None:
        """Reject an assignment of an unknown role."""
        response = self._assign(_MISSING_ID)

        self.assertEqual(response.status_code, 400)
        self.assertIn("role_id", response.json())

    def test_assign_role_to_missing_player_returns_404(self) -> None:
        """Return 404 when the player does not exist."""
        response = self._assign(
            self.role.id, f"{_PLAYER_BASE}/{_MISSING_ID}/role/"
        )

        self.assertEqual(response.status_code, 404)

    def test_assign_role_twice_returns_409(self) -> None:
        """Reject assigning the same role twice."""
        PlayerRole.objects.create(player=self.player, role=self.role)

        response = self._assign(self.role.id)

        self.assertEqual(response.status_code, 409)

    def test_remove_role_returns_204(self) -> None:
        """Remove a role from the player."""
        PlayerRole.objects.create(player=self.player, role=self.role)

        response = self.client.delete(
            f"{self.url}{self.role.id}/", **self.auth
        )

        self.assertEqual(response.status_code, 204)
        self.assertFalse(PlayerRole.objects.exists())

    def test_remove_unassigned_role_returns_404(self) -> None:
        """Return 404 when the player does not have the role."""
        response = self.client.delete(
            f"{self.url}{self.role.id}/", **self.auth
        )

        self.assertEqual(response.status_code, 404)

    def test_remove_role_without_token_returns_401(self) -> None:
        """Reject removal without authentication."""
        response = self.client.delete(f"{self.url}{self.role.id}/")

        self.assertEqual(response.status_code, 401)

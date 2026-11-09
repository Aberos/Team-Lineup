"""Tests for the players API views."""

import json
import shutil
import tempfile
from datetime import date
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import Client, TestCase, override_settings
from django.test.client import BOUNDARY, MULTIPART_CONTENT, encode_multipart
from PIL import Image
from rest_framework_simplejwt.tokens import AccessToken

from apps.players.models import (
    Attribute,
    Player,
    PlayerAttribute,
    PlayerRole,
    Role,
)

_BASE = "/api/v1/role"


def _image(name: str, image_format: str) -> SimpleUploadedFile:
    """Return a small image upload in the given format."""
    buffer = BytesIO()
    Image.new("RGB", (4, 4), "white").save(buffer, format=image_format)
    return SimpleUploadedFile(
        name, buffer.getvalue(), f"image/{image_format.lower()}"
    )


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
        """List players ordered by name inside a page."""
        self._create_player(name="Carla", email="carla@example.com")
        self._create_player(name="Bruno")

        response = self.client.get(f"{_PLAYER_BASE}/", **self.auth)

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(
            (body["count"], body["page"], body["page_size"]), (2, 1, 24)
        )
        self.assertIsNone(body["next"])
        self.assertEqual(
            [player["name"] for player in body["results"]],
            ["Bruno", "Carla"],
        )

    def test_list_players_returns_card_data(self) -> None:
        """Return overall, roles, card attributes and photo of each card."""
        player = self._create_player()
        role = Role.objects.create(name="MID")
        PlayerRole.objects.create(player=player, role=role, is_primary=True)
        attribute = Attribute.objects.create(
            name="Passe", abbreviation="PAS", card_order=1
        )
        PlayerAttribute.objects.create(
            player=player, attribute=attribute, value=82
        )
        Player.objects.filter(id=player.id).update(overall=82)

        response = self.client.get(f"{_PLAYER_BASE}/", **self.auth)

        card = response.json()["results"][0]
        self.assertEqual(
            card,
            {
                "id": player.id,
                "name": "Bruno Lima",
                "number": 7,
                "overall": 82,
                "photo_url": None,
                "roles": [{"id": role.id, "name": "MID", "is_primary": True}],
                "card_attributes": [
                    {"abbreviation": "PAS", "name": "Passe", "value": 82}
                ],
            },
        )

    def test_list_players_paginates_with_links(self) -> None:
        """Split players in pages and link the neighbours."""
        for index in range(3):
            self._create_player(
                name=f"Jogador {index}", email=f"j{index}@example.com"
            )

        first = self.client.get(
            f"{_PLAYER_BASE}/?page_size=2", **self.auth
        ).json()
        second = self.client.get(
            f"{_PLAYER_BASE}/?page_size=2&page=2", **self.auth
        ).json()

        self.assertEqual(len(first["results"]), 2)
        self.assertIn("page=2", first["next"])
        self.assertIsNone(first["previous"])
        self.assertEqual(
            [player["name"] for player in second["results"]], ["Jogador 2"]
        )
        self.assertIsNone(second["next"])
        self.assertIn("page=1", second["previous"])

    def test_list_players_filters_and_orders(self) -> None:
        """Filter by name and role and order by overall."""
        ana = self._create_player(name="Ana", email="ana@example.com")
        bruno = self._create_player()
        Player.objects.filter(id=ana.id).update(overall=70)
        Player.objects.filter(id=bruno.id).update(overall=90)
        role = Role.objects.create(name="DEF")
        PlayerRole.objects.create(player=ana, role=role, is_primary=True)

        def names(query: str) -> list[str]:
            response = self.client.get(f"{_PLAYER_BASE}/?{query}", **self.auth)
            return [player["name"] for player in response.json()["results"]]

        self.assertEqual(names("search=bru"), ["Bruno Lima"])
        self.assertEqual(names(f"role={role.id}"), ["Ana"])
        self.assertEqual(names("ordering=-overall"), ["Bruno Lima", "Ana"])

    def test_list_players_invalid_query_returns_400(self) -> None:
        """Reject invalid page, page size and ordering."""
        for query in ("page=0", "page_size=101", "ordering=age"):
            with self.subTest(query=query):
                response = self.client.get(
                    f"{_PLAYER_BASE}/?{query}", **self.auth
                )
                self.assertEqual(response.status_code, 400)

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
        """List the roles assigned to the player with the primary flag."""
        PlayerRole.objects.create(
            player=self.player, role=self.role, is_primary=True
        )

        response = self.client.get(self.url, **self.auth)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [{"id": self.role.id, "name": "Goalkeeper", "is_primary": True}],
        )

    def test_set_primary_role_returns_200(self) -> None:
        """Move the primary flag to another role."""
        PlayerRole.objects.create(
            player=self.player, role=self.role, is_primary=True
        )
        other = Role.objects.create(name="Striker")
        PlayerRole.objects.create(player=self.player, role=other)

        response = self.client.patch(
            f"{self.url}{other.id}/",
            json.dumps({"is_primary": True}),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["is_primary"], True)
        self.assertEqual(
            PlayerRole.objects.get(is_primary=True).role_id, other.id
        )

    def test_set_primary_role_invalid_returns_400(self) -> None:
        """Reject a payload that does not mark the role as primary."""
        PlayerRole.objects.create(player=self.player, role=self.role)

        for body in ({}, {"is_primary": False}):
            with self.subTest(body=body):
                response = self.client.patch(
                    f"{self.url}{self.role.id}/",
                    json.dumps(body),
                    content_type="application/json",
                    **self.auth,
                )
                self.assertEqual(response.status_code, 400)

    def test_set_primary_on_unassigned_role_returns_404(self) -> None:
        """Return 404 when the player does not have the role."""
        response = self.client.patch(
            f"{self.url}{self.role.id}/",
            json.dumps({"is_primary": True}),
            content_type="application/json",
            **self.auth,
        )

        self.assertEqual(response.status_code, 404)

    def test_set_primary_role_without_token_returns_401(self) -> None:
        """Reject the change without authentication."""
        response = self.client.patch(
            f"{self.url}{self.role.id}/",
            json.dumps({"is_primary": True}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

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


_ATTRIBUTE_BASE = "/api/v1/attribute"


class _AuthenticatedTestCase(TestCase):
    """Provide an authenticated JSON client for the attribute tests."""

    def setUp(self) -> None:
        self.client = Client()
        user = get_user_model().objects.create_user(
            username="tester", password="secret-pass"
        )
        self.auth = {
            "HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(user)}"
        }

    def send(self, method: str, url: str, body: object) -> HttpResponse:
        """Send an authenticated JSON request."""
        return getattr(self.client, method)(
            url,
            json.dumps(body),
            content_type="application/json",
            **self.auth,
        )


_ATTRIBUTE_PAYLOAD = {"name": "Passe", "abbreviation": "pas", "card_order": 1}


class AttributeViewTests(_AuthenticatedTestCase):
    """Tests for the attribute catalog endpoints."""

    def test_list_attributes_ordered_by_name(self) -> None:
        """List attributes ordered by name with card fields."""
        Attribute.objects.create(name="Velocidade", abbreviation="VEL")
        passe = Attribute.objects.create(
            name="Passe", abbreviation="PAS", card_order=2
        )

        response = self.client.get(f"{_ATTRIBUTE_BASE}/", **self.auth)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()[0],
            {
                "id": passe.id,
                "name": "Passe",
                "abbreviation": "PAS",
                "card_order": 2,
            },
        )
        self.assertEqual(response.json()[1]["card_order"], None)

    def test_list_attributes_without_token_returns_401(self) -> None:
        """Reject listing without authentication."""
        response = self.client.get(f"{_ATTRIBUTE_BASE}/")

        self.assertEqual(response.status_code, 401)

    def test_create_attribute_returns_201(self) -> None:
        """Create an attribute with uppercase abbreviation."""
        response = self.send("post", f"{_ATTRIBUTE_BASE}/", _ATTRIBUTE_PAYLOAD)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            (response.json()["abbreviation"], response.json()["card_order"]),
            ("PAS", 1),
        )

    def test_create_attribute_off_card_by_default(self) -> None:
        """Keep the attribute off the cards without card_order."""
        response = self.send(
            "post",
            f"{_ATTRIBUTE_BASE}/",
            {"name": "Liderança", "abbreviation": "LID"},
        )

        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.json()["card_order"])

    def test_create_attribute_invalid_returns_400(self) -> None:
        """Reject missing fields, bad abbreviations and card slots."""
        invalid_payloads = [
            {},
            {"name": "Passe"},
            {**_ATTRIBUTE_PAYLOAD, "abbreviation": "PASSE"},
            {**_ATTRIBUTE_PAYLOAD, "abbreviation": "P4S"},
            {**_ATTRIBUTE_PAYLOAD, "card_order": 0},
            {**_ATTRIBUTE_PAYLOAD, "card_order": 7},
        ]

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.send("post", f"{_ATTRIBUTE_BASE}/", payload)
                self.assertEqual(response.status_code, 400)

    def test_create_attribute_conflicts_return_409(self) -> None:
        """Reject a repeated name, abbreviation or card slot."""
        Attribute.objects.create(
            name="Passe", abbreviation="PAS", card_order=1
        )
        cases = [
            ({**_ATTRIBUTE_PAYLOAD, "name": "passe"}, "name"),
            (
                {**_ATTRIBUTE_PAYLOAD, "name": "Lançamento", "card_order": 2},
                "abbreviation",
            ),
            (
                {
                    "name": "Lançamento",
                    "abbreviation": "LAN",
                    "card_order": 1,
                },
                "card_order",
            ),
        ]

        for payload, field in cases:
            with self.subTest(field=field):
                response = self.send("post", f"{_ATTRIBUTE_BASE}/", payload)
                self.assertEqual(response.status_code, 409)
                self.assertIn(field, response.json())

    def test_get_update_and_delete_attribute(self) -> None:
        """Run the read, update and delete flow of an attribute."""
        attribute = Attribute.objects.create(
            name="Passe", abbreviation="PAS", card_order=1
        )
        url = f"{_ATTRIBUTE_BASE}/{attribute.id}/"

        self.assertEqual(self.client.get(url, **self.auth).status_code, 200)
        updated = self.send(
            "put",
            url,
            {"name": "Passe longo", "abbreviation": "PSL", "card_order": None},
        )
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(
            (updated.json()["name"], updated.json()["card_order"]),
            ("Passe longo", None),
        )
        self.assertEqual(self.client.delete(url, **self.auth).status_code, 204)
        self.assertFalse(Attribute.objects.exists())

    def test_update_to_existing_name_returns_409(self) -> None:
        """Reject renaming to the name of another attribute."""
        Attribute.objects.create(name="Passe", abbreviation="PAS")
        other = Attribute.objects.create(name="Chute", abbreviation="CHU")

        response = self.send(
            "put",
            f"{_ATTRIBUTE_BASE}/{other.id}/",
            {"name": "Passe", "abbreviation": "CHU"},
        )

        self.assertEqual(response.status_code, 409)

    def test_update_attribute_invalid_returns_400(self) -> None:
        """Reject an update without the required fields."""
        attribute = Attribute.objects.create(name="Passe", abbreviation="PAS")

        response = self.send("put", f"{_ATTRIBUTE_BASE}/{attribute.id}/", {})

        self.assertEqual(response.status_code, 400)

    def test_missing_attribute_returns_404(self) -> None:
        """Return 404 for an unknown attribute."""
        url = f"{_ATTRIBUTE_BASE}/{_MISSING_ID}/"

        self.assertEqual(self.client.get(url, **self.auth).status_code, 404)
        self.assertEqual(
            self.send("put", url, _ATTRIBUTE_PAYLOAD).status_code, 404
        )
        self.assertEqual(self.client.delete(url, **self.auth).status_code, 404)


class PlayerAttributeViewTests(_AuthenticatedTestCase):
    """Tests for the player rating endpoints."""

    def setUp(self) -> None:
        super().setUp()
        self.player = Player.objects.create(
            name="Ana",
            birthday=date(1995, 4, 10),
            phone="11999990000",
            email="ana@example.com",
            number=10,
        )
        self.attribute = Attribute.objects.create(
            name="Passe", abbreviation="PAS", card_order=1
        )
        self.url = f"{_PLAYER_BASE}/{self.player.id}/attribute/"
        self.detail_url = f"{self.url}{self.attribute.id}/"

    def _rate(self, value: int) -> PlayerAttribute:
        """Persist a rating for the fixture player and attribute."""
        return PlayerAttribute.objects.create(
            player=self.player, attribute=self.attribute, value=value
        )

    def test_rate_player_returns_201(self) -> None:
        """Rate the player in an attribute."""
        response = self.send(
            "post", self.url, {"attribute_id": self.attribute.id, "value": 80}
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "attribute": {
                    "id": self.attribute.id,
                    "name": "Passe",
                    "abbreviation": "PAS",
                    "card_order": 1,
                },
                "value": 80,
            },
        )

    def test_rate_player_out_of_range_returns_400(self) -> None:
        """Reject values outside 0 to 100 and missing fields."""
        invalid_payloads = [
            {"attribute_id": self.attribute.id, "value": -1},
            {"attribute_id": self.attribute.id, "value": 101},
            {"attribute_id": self.attribute.id},
            {"value": 50},
        ]

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.send("post", self.url, payload)
                self.assertEqual(response.status_code, 400)

    def test_rate_with_missing_attribute_returns_400(self) -> None:
        """Reject an unknown attribute."""
        response = self.send(
            "post", self.url, {"attribute_id": _MISSING_ID, "value": 50}
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("attribute_id", response.json())

    def test_rate_missing_player_returns_404(self) -> None:
        """Return 404 for an unknown player."""
        response = self.send(
            "post",
            f"{_PLAYER_BASE}/{_MISSING_ID}/attribute/",
            {"attribute_id": self.attribute.id, "value": 50},
        )

        self.assertEqual(response.status_code, 404)

    def test_rate_twice_returns_409(self) -> None:
        """Reject a second rating for the same attribute."""
        self._rate(50)

        response = self.send(
            "post", self.url, {"attribute_id": self.attribute.id, "value": 60}
        )

        self.assertEqual(response.status_code, 409)

    def test_rate_without_token_returns_401(self) -> None:
        """Reject rating without authentication."""
        response = self.client.post(
            self.url,
            json.dumps({"attribute_id": self.attribute.id, "value": 50}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

    def test_list_ratings_returns_200(self) -> None:
        """List the ratings of the player."""
        self._rate(70)

        response = self.client.get(self.url, **self.auth)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["value"], 70)

    def test_list_ratings_of_missing_player_returns_404(self) -> None:
        """Return 404 for an unknown player."""
        response = self.client.get(
            f"{_PLAYER_BASE}/{_MISSING_ID}/attribute/", **self.auth
        )

        self.assertEqual(response.status_code, 404)

    def test_get_update_and_delete_rating(self) -> None:
        """Run the read, update and delete flow of a rating."""
        self._rate(40)

        self.assertEqual(
            self.client.get(self.detail_url, **self.auth).json()["value"], 40
        )
        updated = self.send("put", self.detail_url, {"value": 95})
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["value"], 95)
        deleted = self.client.delete(self.detail_url, **self.auth)
        self.assertEqual(deleted.status_code, 204)
        self.assertFalse(PlayerAttribute.objects.exists())

    def test_update_rating_out_of_range_returns_400(self) -> None:
        """Reject an update above 100."""
        self._rate(40)

        response = self.send("put", self.detail_url, {"value": 150})

        self.assertEqual(response.status_code, 400)

    def test_missing_rating_returns_404(self) -> None:
        """Return 404 when the player has no rating for the attribute."""
        self.assertEqual(
            self.client.get(self.detail_url, **self.auth).status_code, 404
        )
        self.assertEqual(
            self.send("put", self.detail_url, {"value": 10}).status_code, 404
        )
        self.assertEqual(
            self.client.delete(self.detail_url, **self.auth).status_code, 404
        )

    def test_delete_attribute_removes_ratings(self) -> None:
        """Remove the ratings when the attribute is deleted."""
        self._rate(40)

        self.client.delete(
            f"{_ATTRIBUTE_BASE}/{self.attribute.id}/", **self.auth
        )

        self.assertFalse(PlayerAttribute.objects.exists())


class PlayerPhotoViewTests(_AuthenticatedTestCase):
    """Tests for the player photo endpoint."""

    def setUp(self) -> None:
        super().setUp()
        media_root = tempfile.mkdtemp()
        override = override_settings(MEDIA_ROOT=media_root)
        override.enable()
        self.addCleanup(override.disable)
        self.addCleanup(shutil.rmtree, media_root, True)
        self.player = Player.objects.create(
            name="Ana",
            birthday=date(1995, 4, 10),
            phone="11999990000",
            email="ana@example.com",
            number=10,
        )
        self.url = f"{_PLAYER_BASE}/{self.player.id}/photo/"

    def _upload(
        self, upload: SimpleUploadedFile, url: str = ""
    ) -> HttpResponse:
        """Send a multipart PUT with the photo."""
        return self.client.put(
            url or self.url,
            encode_multipart(BOUNDARY, {"photo": upload}),
            content_type=MULTIPART_CONTENT,
            **self.auth,
        )

    def test_upload_and_remove_photo(self) -> None:
        """Store the photo, expose its URL and remove it."""
        response = self._upload(_image("ana.png", "PNG"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response.json()["photo_url"].startswith("/media/players/")
        )

        removed = self.client.delete(self.url, **self.auth)
        self.assertEqual(removed.status_code, 200)
        self.assertIsNone(removed.json()["photo_url"])

    def test_upload_invalid_photo_returns_400(self) -> None:
        """Reject files that are not images, other formats and big files."""
        not_image = SimpleUploadedFile("a.png", b"text", "image/png")
        gif = _image("a.gif", "GIF")
        big = SimpleUploadedFile(
            "big.png",
            _image("x.png", "PNG").read() + b"0" * (2 * 1024 * 1024),
            "image/png",
        )

        for upload in (not_image, gif, big):
            with self.subTest(name=upload.name):
                self.assertEqual(self._upload(upload).status_code, 400)

    def test_photo_of_missing_player_returns_404(self) -> None:
        """Return 404 for an unknown player."""
        url = f"{_PLAYER_BASE}/{_MISSING_ID}/photo/"

        self.assertEqual(
            self._upload(_image("a.png", "PNG"), url).status_code, 404
        )
        self.assertEqual(self.client.delete(url, **self.auth).status_code, 404)

    def test_photo_without_token_returns_401(self) -> None:
        """Reject the upload without authentication."""
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 401)


_FORMULA_BASE = "/api/v1/overall-formula"
_FORMULA_SCRIPT = "function overall(notas) return (notas.PAS or 0) + 5 end"


class OverallFormulaViewTests(TestCase):
    """Tests for the overall formula endpoints."""

    def setUp(self) -> None:
        self.client = Client()
        admin = get_user_model().objects.create_user(
            username="admin", password="secret-pass", is_staff=True
        )
        member = get_user_model().objects.create_user(
            username="member", password="secret-pass"
        )
        self.admin = {
            "HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(admin)}"
        }
        self.member = {
            "HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(member)}"
        }
        self.player = Player.objects.create(
            name="Ana",
            birthday=date(1995, 4, 10),
            phone="1",
            email="ana@example.com",
            number=10,
            overall=70,
        )
        attribute = Attribute.objects.create(
            name="Passe", abbreviation="PAS", card_order=1
        )
        PlayerAttribute.objects.create(
            player=self.player, attribute=attribute, value=70
        )

    def _post(
        self, url: str, body: object, auth: dict[str, str]
    ) -> HttpResponse:
        """Send an authenticated JSON POST."""
        return self.client.post(
            url, json.dumps(body), content_type="application/json", **auth
        )

    def _create(self, script: str = _FORMULA_SCRIPT) -> HttpResponse:
        """Create a formula as administrator."""
        return self._post(
            f"{_FORMULA_BASE}/",
            {"script": script, "description": "Passe +5"},
            self.admin,
        )

    def test_requires_authentication_and_staff(self) -> None:
        """Return 401 without token and 403 for regular users."""
        urls = [
            f"{_FORMULA_BASE}/",
            f"{_FORMULA_BASE}/active/",
        ]

        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 401)
                self.assertEqual(
                    self.client.get(url, **self.member).status_code, 403
                )
        self.assertEqual(
            self._post(
                f"{_FORMULA_BASE}/preview/",
                {"script": _FORMULA_SCRIPT},
                self.member,
            ).status_code,
            403,
        )

    def test_create_and_list_formula(self) -> None:
        """Create an inactive version with author and list it."""
        response = self._create()

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(
            (body["is_active"], body["created_by"], body["description"]),
            (False, "admin", "Passe +5"),
        )
        listed = self.client.get(f"{_FORMULA_BASE}/", **self.admin).json()
        self.assertEqual([item["id"] for item in listed], [body["id"]])

    def test_create_invalid_formula_returns_400(self) -> None:
        """Reject missing scripts and scripts that do not compile."""
        for body in ({}, {"script": "function overall( return"}):
            with self.subTest(body=body):
                response = self._post(f"{_FORMULA_BASE}/", body, self.admin)
                self.assertEqual(response.status_code, 400)
                self.assertIn("script", response.json())

    def test_preview_returns_results_per_player(self) -> None:
        """Return current and new overall without saving."""
        response = self._post(
            f"{_FORMULA_BASE}/preview/",
            {"script": _FORMULA_SCRIPT, "limit": 5},
            self.admin,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            [
                {
                    "player_id": self.player.id,
                    "player_name": "Ana",
                    "current_overall": 70,
                    "new_overall": 75,
                    "error": None,
                }
            ],
        )

    def test_preview_invalid_returns_400(self) -> None:
        """Reject broken scripts and limits out of range."""
        for body in (
            {"script": "x = "},
            {"script": _FORMULA_SCRIPT, "limit": 0},
        ):
            with self.subTest(body=body):
                response = self._post(
                    f"{_FORMULA_BASE}/preview/", body, self.admin
                )
                self.assertEqual(response.status_code, 400)

    def test_activate_show_and_deactivate(self) -> None:
        """Activate, read the active one and go back to the average."""
        formula_id = self._create().json()["id"]

        activated = self._post(
            f"{_FORMULA_BASE}/{formula_id}/activate/", {}, self.admin
        )

        self.assertEqual(activated.status_code, 200)
        self.player.refresh_from_db()
        self.assertEqual(self.player.overall, 75)
        active = self.client.get(f"{_FORMULA_BASE}/active/", **self.admin)
        self.assertEqual(active.json()["formula"]["id"], formula_id)

        removed = self.client.delete(f"{_FORMULA_BASE}/active/", **self.admin)

        self.assertEqual(removed.status_code, 204)
        self.player.refresh_from_db()
        self.assertEqual(self.player.overall, 70)
        self.assertIsNone(
            self.client.get(f"{_FORMULA_BASE}/active/", **self.admin).json()[
                "formula"
            ]
        )

    def test_activate_failing_formula_returns_409(self) -> None:
        """List the players for which the formula failed."""
        formula_id = self._create(
            "function overall() error('quebrou') end"
        ).json()["id"]

        response = self._post(
            f"{_FORMULA_BASE}/{formula_id}/activate/", {}, self.admin
        )

        self.assertEqual(response.status_code, 409)
        failure = response.json()["failures"][0]
        self.assertEqual(failure["player_name"], "Ana")
        self.assertIn("quebrou", failure["error"])

    def test_detail_and_delete_rules(self) -> None:
        """Read, refuse deleting the active one and delete inactive ones."""
        formula_id = self._create().json()["id"]
        url = f"{_FORMULA_BASE}/{formula_id}/"
        self._post(f"{url}activate/", {}, self.admin)

        self.assertEqual(self.client.get(url, **self.admin).status_code, 200)
        self.assertEqual(
            self.client.delete(url, **self.admin).status_code, 409
        )
        self.client.delete(f"{_FORMULA_BASE}/active/", **self.admin)
        self.assertEqual(
            self.client.delete(url, **self.admin).status_code, 204
        )

    def test_missing_formula_returns_404(self) -> None:
        """Return 404 for an unknown formula."""
        url = f"{_FORMULA_BASE}/{_MISSING_ID}/"

        self.assertEqual(self.client.get(url, **self.admin).status_code, 404)
        self.assertEqual(
            self.client.delete(url, **self.admin).status_code, 404
        )
        self.assertEqual(
            self._post(f"{url}activate/", {}, self.admin).status_code, 404
        )

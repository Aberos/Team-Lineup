"""Tests for the events API views."""

import json
from datetime import date

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, TestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.events.models import (
    Event,
    EventMatch,
    EventParticipation,
    EventTeam,
    MatchStatus,
    TeamMembership,
)
from apps.players.models import Player

_BASE = "/api/v1/event"
_MISSING_ID = 999_999


class _EventApiTestCase(TestCase):
    """Provide authentication and fixtures for the events API tests."""

    def setUp(self) -> None:
        self.client = Client()
        user = get_user_model().objects.create_user(
            username="tester", password="secret-pass"
        )
        self.auth = {
            "HTTP_AUTHORIZATION": f"Bearer {AccessToken.for_user(user)}"
        }
        self.event = Event.objects.create(
            name="Copa", date=date(2026, 5, 1), location="Arena"
        )
        self.player = Player.objects.create(
            name="Ana",
            birthday=date(1995, 4, 10),
            phone="11999990000",
            email="ana@example.com",
            number=10,
        )
        self.event_url = f"{_BASE}/{self.event.id}"

    def send(self, method: str, url: str, body: object) -> HttpResponse:
        """Send an authenticated JSON request."""
        return getattr(self.client, method)(
            url,
            json.dumps(body),
            content_type="application/json",
            **self.auth,
        )

    def get(self, url: str) -> HttpResponse:
        """Send an authenticated GET request."""
        return self.client.get(url, **self.auth)

    def delete(self, url: str) -> HttpResponse:
        """Send an authenticated DELETE request."""
        return self.client.delete(url, **self.auth)


class EventViewTests(_EventApiTestCase):
    """Tests for the event endpoints."""

    _PAYLOAD = {"name": "Liga", "date": "2026-06-01", "location": "Campo"}

    def test_list_events_returns_200(self) -> None:
        """List events, most recent first."""
        Event.objects.create(
            name="Antigo", date=date(2020, 1, 1), location="X"
        )

        response = self.get(f"{_BASE}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [event["name"] for event in response.json()], ["Copa", "Antigo"]
        )

    def test_list_events_without_token_returns_401(self) -> None:
        """Reject listing without authentication."""
        self.assertEqual(self.client.get(f"{_BASE}/").status_code, 401)

    def test_create_event_returns_201(self) -> None:
        """Create an event."""
        response = self.send("post", f"{_BASE}/", self._PAYLOAD)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["date"], "2026-06-01")

    def test_create_event_invalid_returns_400(self) -> None:
        """Reject an event with an invalid date."""
        response = self.send(
            "post", f"{_BASE}/", {**self._PAYLOAD, "date": "invalid"}
        )

        self.assertEqual(response.status_code, 400)

    def test_get_event_returns_200(self) -> None:
        """Return the requested event."""
        response = self.get(f"{self.event_url}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Copa")

    def test_get_missing_event_returns_404(self) -> None:
        """Return 404 for an unknown event."""
        self.assertEqual(self.get(f"{_BASE}/{_MISSING_ID}/").status_code, 404)

    def test_update_event_returns_200(self) -> None:
        """Replace the data of an event."""
        response = self.send("put", f"{self.event_url}/", self._PAYLOAD)

        self.assertEqual(response.status_code, 200)
        self.event.refresh_from_db()
        self.assertEqual(self.event.location, "Campo")

    def test_update_event_invalid_returns_400(self) -> None:
        """Reject an update with missing fields."""
        response = self.send("put", f"{self.event_url}/", {"name": "X"})

        self.assertEqual(response.status_code, 400)

    def test_update_missing_event_returns_404(self) -> None:
        """Return 404 when updating an unknown event."""
        response = self.send("put", f"{_BASE}/{_MISSING_ID}/", self._PAYLOAD)

        self.assertEqual(response.status_code, 404)

    def test_delete_event_returns_204(self) -> None:
        """Delete the requested event."""
        response = self.delete(f"{self.event_url}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())

    def test_delete_missing_event_returns_404(self) -> None:
        """Return 404 when deleting an unknown event."""
        self.assertEqual(
            self.delete(f"{_BASE}/{_MISSING_ID}/").status_code, 404
        )


class EventParticipantViewTests(_EventApiTestCase):
    """Tests for the event participant endpoints."""

    def setUp(self) -> None:
        super().setUp()
        self.url = f"{self.event_url}/participant/"

    def test_add_participant_returns_201(self) -> None:
        """Register a player with default score."""
        response = self.send("post", self.url, {"player_id": self.player.id})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["score"], 0)
        self.assertEqual(response.json()["player"]["id"], self.player.id)

    def test_add_participant_without_player_returns_400(self) -> None:
        """Reject a payload without player identifier."""
        self.assertEqual(self.send("post", self.url, {}).status_code, 400)

    def test_add_missing_player_returns_400(self) -> None:
        """Reject an unknown player."""
        response = self.send("post", self.url, {"player_id": _MISSING_ID})

        self.assertEqual(response.status_code, 400)
        self.assertIn("player_id", response.json())

    def test_add_participant_to_missing_event_returns_404(self) -> None:
        """Return 404 for an unknown event."""
        response = self.send(
            "post",
            f"{_BASE}/{_MISSING_ID}/participant/",
            {"player_id": self.player.id},
        )

        self.assertEqual(response.status_code, 404)

    def test_add_participant_twice_returns_409(self) -> None:
        """Reject registering the same player twice."""
        EventParticipation.objects.create(
            event=self.event, player=self.player, score=0
        )

        response = self.send("post", self.url, {"player_id": self.player.id})

        self.assertEqual(response.status_code, 409)

    def test_add_participant_without_token_returns_401(self) -> None:
        """Reject registration without authentication."""
        response = self.client.post(
            self.url,
            json.dumps({"player_id": self.player.id}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

    def test_list_participants_returns_200(self) -> None:
        """List the participants of the event."""
        EventParticipation.objects.create(
            event=self.event, player=self.player, score=3
        )

        response = self.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["score"], 3)

    def test_list_participants_of_missing_event_returns_404(self) -> None:
        """Return 404 for an unknown event."""
        response = self.get(f"{_BASE}/{_MISSING_ID}/participant/")

        self.assertEqual(response.status_code, 404)

    def test_get_and_update_participant(self) -> None:
        """Return and change the score of a participant."""
        EventParticipation.objects.create(
            event=self.event, player=self.player, score=0
        )
        detail_url = f"{self.url}{self.player.id}/"

        self.assertEqual(self.get(detail_url).status_code, 200)
        response = self.send("put", detail_url, {"score": 5})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["score"], 5)

    def test_update_participant_invalid_returns_400(self) -> None:
        """Reject an update without score."""
        EventParticipation.objects.create(
            event=self.event, player=self.player, score=0
        )

        response = self.send("put", f"{self.url}{self.player.id}/", {})

        self.assertEqual(response.status_code, 400)

    def test_missing_participant_returns_404(self) -> None:
        """Return 404 for a player that is not a participant."""
        detail_url = f"{self.url}{self.player.id}/"

        self.assertEqual(self.get(detail_url).status_code, 404)
        self.assertEqual(
            self.send("put", detail_url, {"score": 1}).status_code, 404
        )
        self.assertEqual(self.delete(detail_url).status_code, 404)

    def test_remove_participant_also_leaves_teams(self) -> None:
        """Remove the participant and its team memberships."""
        EventParticipation.objects.create(
            event=self.event, player=self.player, score=0
        )
        team = EventTeam.objects.create(event=self.event, team_name="A")
        TeamMembership.objects.create(team=team, participant=self.player)

        response = self.delete(f"{self.url}{self.player.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(EventParticipation.objects.exists())
        self.assertFalse(TeamMembership.objects.exists())


class EventTeamViewTests(_EventApiTestCase):
    """Tests for the event team and member endpoints."""

    def setUp(self) -> None:
        super().setUp()
        self.url = f"{self.event_url}/team/"
        self.team = EventTeam.objects.create(event=self.event, team_name="A")
        self.member_url = f"{self.url}{self.team.id}/member/"

    def test_create_team_returns_201(self) -> None:
        """Create a team in the event."""
        response = self.send("post", self.url, {"team_name": "B"})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["team_name"], "B")

    def test_create_team_without_name_returns_400(self) -> None:
        """Reject a team without name."""
        self.assertEqual(self.send("post", self.url, {}).status_code, 400)

    def test_create_team_duplicated_name_returns_409(self) -> None:
        """Reject a second team with the same name in the event."""
        response = self.send("post", self.url, {"team_name": "A"})

        self.assertEqual(response.status_code, 409)

    def test_create_team_in_missing_event_returns_404(self) -> None:
        """Return 404 for an unknown event."""
        response = self.send(
            "post", f"{_BASE}/{_MISSING_ID}/team/", {"team_name": "B"}
        )

        self.assertEqual(response.status_code, 404)

    def test_create_team_without_token_returns_401(self) -> None:
        """Reject creation without authentication."""
        response = self.client.post(
            self.url,
            json.dumps({"team_name": "B"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)

    def test_list_get_rename_and_delete_team(self) -> None:
        """Run the read, update and delete flow of a team."""
        detail_url = f"{self.url}{self.team.id}/"

        self.assertEqual(len(self.get(self.url).json()), 1)
        self.assertEqual(self.get(detail_url).json()["team_name"], "A")
        renamed = self.send("put", detail_url, {"team_name": "Azul"})
        self.assertEqual(renamed.status_code, 200)
        self.assertEqual(renamed.json()["team_name"], "Azul")
        self.assertEqual(self.delete(detail_url).status_code, 204)
        self.assertFalse(EventTeam.objects.exists())

    def test_rename_team_to_existing_name_returns_409(self) -> None:
        """Reject renaming to the name of another team."""
        other = EventTeam.objects.create(event=self.event, team_name="B")

        response = self.send(
            "put", f"{self.url}{other.id}/", {"team_name": "A"}
        )

        self.assertEqual(response.status_code, 409)

    def test_team_of_other_event_returns_404(self) -> None:
        """Return 404 for a team that belongs to another event."""
        other_event = Event.objects.create(
            name="Outro", date=date(2026, 1, 1), location="Y"
        )
        detail_url = f"{_BASE}/{other_event.id}/team/{self.team.id}/"

        self.assertEqual(self.get(detail_url).status_code, 404)
        self.assertEqual(
            self.send("put", detail_url, {"team_name": "Z"}).status_code,
            404,
        )
        self.assertEqual(self.delete(detail_url).status_code, 404)

    def test_add_member_returns_201(self) -> None:
        """Add an event participant to the team."""
        EventParticipation.objects.create(
            event=self.event, player=self.player, score=0
        )

        response = self.send(
            "post", self.member_url, {"player_id": self.player.id}
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["player"]["name"], "Ana")
        self.assertEqual(len(self.get(self.member_url).json()), 1)

    def test_add_member_without_player_returns_400(self) -> None:
        """Reject a payload without player identifier."""
        response = self.send("post", self.member_url, {})

        self.assertEqual(response.status_code, 400)

    def test_add_missing_player_as_member_returns_400(self) -> None:
        """Reject an unknown player."""
        response = self.send(
            "post", self.member_url, {"player_id": _MISSING_ID}
        )

        self.assertEqual(response.status_code, 400)

    def test_add_member_to_missing_team_returns_404(self) -> None:
        """Return 404 for an unknown team."""
        response = self.send(
            "post",
            f"{self.url}{_MISSING_ID}/member/",
            {"player_id": self.player.id},
        )

        self.assertEqual(response.status_code, 404)

    def test_add_non_participant_returns_409(self) -> None:
        """Reject a player that does not participate in the event."""
        response = self.send(
            "post", self.member_url, {"player_id": self.player.id}
        )

        self.assertEqual(response.status_code, 409)

    def test_add_member_already_in_other_team_returns_409(self) -> None:
        """Reject a player that already plays for a team of the event."""
        EventParticipation.objects.create(
            event=self.event, player=self.player, score=0
        )
        other = EventTeam.objects.create(event=self.event, team_name="B")
        TeamMembership.objects.create(team=other, participant=self.player)

        response = self.send(
            "post", self.member_url, {"player_id": self.player.id}
        )

        self.assertEqual(response.status_code, 409)

    def test_remove_member(self) -> None:
        """Remove a member and return 404 when it is gone."""
        TeamMembership.objects.create(team=self.team, participant=self.player)
        detail_url = f"{self.member_url}{self.player.id}/"

        self.assertEqual(self.delete(detail_url).status_code, 204)
        self.assertEqual(self.delete(detail_url).status_code, 404)

    def test_members_without_token_returns_401(self) -> None:
        """Reject member listing without authentication."""
        self.assertEqual(self.client.get(self.member_url).status_code, 401)


class EventMatchViewTests(_EventApiTestCase):
    """Tests for the event match endpoints."""

    def setUp(self) -> None:
        super().setUp()
        self.url = f"{self.event_url}/match/"
        self.home = EventTeam.objects.create(event=self.event, team_name="A")
        self.away = EventTeam.objects.create(event=self.event, team_name="B")
        self.payload = {
            "team_home_id": self.home.id,
            "team_away_id": self.away.id,
        }

    def _create_match(self) -> EventMatch:
        """Persist a scheduled match between the fixture teams."""
        return EventMatch.objects.create(
            event=self.event,
            team_home=self.home,
            team_away=self.away,
            score_team_home=0,
            score_team_away=0,
        )

    def test_create_match_returns_201_with_defaults(self) -> None:
        """Create a scheduled match with zero scores."""
        response = self.send("post", self.url, self.payload)

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["status"], MatchStatus.SCHEDULED)
        self.assertEqual(body["team_home"]["team_name"], "A")
        self.assertEqual(body["score_team_away"], 0)

    def test_create_match_invalid_returns_400(self) -> None:
        """Reject same teams, negative scores and invalid status."""
        invalid_payloads = [
            {**self.payload, "team_away_id": self.home.id},
            {**self.payload, "score_team_home": -1},
            {**self.payload, "status": 99},
            {},
        ]

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                response = self.send("post", self.url, payload)
                self.assertEqual(response.status_code, 400)

    def test_create_match_with_team_of_other_event_returns_400(self) -> None:
        """Reject a team that does not belong to the event."""
        other_event = Event.objects.create(
            name="Outro", date=date(2026, 1, 1), location="Y"
        )
        foreign = EventTeam.objects.create(event=other_event, team_name="C")

        response = self.send(
            "post", self.url, {**self.payload, "team_away_id": foreign.id}
        )

        self.assertEqual(response.status_code, 400)

    def test_create_match_in_missing_event_returns_404(self) -> None:
        """Return 404 for an unknown event."""
        response = self.send(
            "post", f"{_BASE}/{_MISSING_ID}/match/", self.payload
        )

        self.assertEqual(response.status_code, 404)

    def test_create_match_without_token_returns_401(self) -> None:
        """Reject creation without authentication."""
        response = self.client.post(
            self.url, json.dumps(self.payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)

    def test_list_and_get_match(self) -> None:
        """List the matches and return one of them."""
        match = self._create_match()

        self.assertEqual(len(self.get(self.url).json()), 1)
        response = self.get(f"{self.url}{match.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], match.id)

    def test_update_match_returns_200(self) -> None:
        """Replace scores and status of a match."""
        match = self._create_match()

        response = self.send(
            "put",
            f"{self.url}{match.id}/",
            {
                "team_home_id": self.away.id,
                "team_away_id": self.home.id,
                "score_team_home": 2,
                "score_team_away": 1,
                "status": MatchStatus.COMPLETED,
            },
        )

        self.assertEqual(response.status_code, 200)
        match.refresh_from_db()
        self.assertEqual(match.status, MatchStatus.COMPLETED)
        self.assertEqual(match.team_home_id, self.away.id)

    def test_update_match_partial_payload_returns_400(self) -> None:
        """Require every field when replacing a match."""
        match = self._create_match()

        response = self.send("put", f"{self.url}{match.id}/", self.payload)

        self.assertEqual(response.status_code, 400)

    def test_missing_match_returns_404(self) -> None:
        """Return 404 for an unknown match."""
        detail_url = f"{self.url}{_MISSING_ID}/"

        self.assertEqual(self.get(detail_url).status_code, 404)
        self.assertEqual(self.delete(detail_url).status_code, 404)

    def test_delete_match_returns_204(self) -> None:
        """Delete the requested match."""
        match = self._create_match()

        response = self.delete(f"{self.url}{match.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(EventMatch.objects.exists())

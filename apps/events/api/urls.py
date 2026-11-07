"""URL patterns for the events app."""

from django.urls import path

from apps.events.api.views import (
    EventDetailView,
    EventListCreateView,
    EventMatchDetailView,
    EventMatchListCreateView,
    EventParticipantDetailView,
    EventParticipantListCreateView,
    EventTeamDetailView,
    EventTeamListCreateView,
    TeamMemberDetailView,
    TeamMemberListCreateView,
)

_BASE_EVENT = "event"
_EVENT_DETAIL = f"{_BASE_EVENT}/<int:event_id>"
_TEAM_DETAIL = f"{_EVENT_DETAIL}/team/<int:team_id>"

urlpatterns = [
    path(
        f"{_BASE_EVENT}/",
        EventListCreateView.as_view(),
        name="events-event-list-create",
    ),
    path(
        f"{_EVENT_DETAIL}/",
        EventDetailView.as_view(),
        name="events-event-detail",
    ),
    path(
        f"{_EVENT_DETAIL}/participant/",
        EventParticipantListCreateView.as_view(),
        name="events-participant-list-create",
    ),
    path(
        f"{_EVENT_DETAIL}/participant/<int:player_id>/",
        EventParticipantDetailView.as_view(),
        name="events-participant-detail",
    ),
    path(
        f"{_EVENT_DETAIL}/team/",
        EventTeamListCreateView.as_view(),
        name="events-team-list-create",
    ),
    path(
        f"{_TEAM_DETAIL}/",
        EventTeamDetailView.as_view(),
        name="events-team-detail",
    ),
    path(
        f"{_TEAM_DETAIL}/member/",
        TeamMemberListCreateView.as_view(),
        name="events-team-member-list-create",
    ),
    path(
        f"{_TEAM_DETAIL}/member/<int:player_id>/",
        TeamMemberDetailView.as_view(),
        name="events-team-member-detail",
    ),
    path(
        f"{_EVENT_DETAIL}/match/",
        EventMatchListCreateView.as_view(),
        name="events-match-list-create",
    ),
    path(
        f"{_EVENT_DETAIL}/match/<int:match_id>/",
        EventMatchDetailView.as_view(),
        name="events-match-detail",
    ),
]

"""URL patterns for the players app."""

from django.urls import path

from apps.players.api.views import (
    PlayerDetailView,
    PlayerListCreateView,
    PlayerRoleDetailView,
    PlayerRoleListCreateView,
    RoleDetailView,
    RoleListCreateView,
)

_BASE_ROLE = "role"
_BASE_PLAYER = "player"

urlpatterns = [
    path(
        f"{_BASE_ROLE}/",
        RoleListCreateView.as_view(),
        name="players-role-list-create",
    ),
    path(
        f"{_BASE_ROLE}/<int:role_id>/",
        RoleDetailView.as_view(),
        name="players-role-detail",
    ),
    path(
        f"{_BASE_PLAYER}/",
        PlayerListCreateView.as_view(),
        name="players-player-list-create",
    ),
    path(
        f"{_BASE_PLAYER}/<int:player_id>/",
        PlayerDetailView.as_view(),
        name="players-player-detail",
    ),
    path(
        f"{_BASE_PLAYER}/<int:player_id>/role/",
        PlayerRoleListCreateView.as_view(),
        name="players-player-role-list-create",
    ),
    path(
        f"{_BASE_PLAYER}/<int:player_id>/role/<int:role_id>/",
        PlayerRoleDetailView.as_view(),
        name="players-player-role-detail",
    ),
]

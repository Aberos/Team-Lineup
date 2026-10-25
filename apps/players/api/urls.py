"""URL patterns for the players app."""

from django.urls import path

from apps.players.api.views import (
    RoleCreateView,
    RoleDeleteView,
    RoleDetailView,
    RoleListView,
    RoleUpdateView,
)

_BASE_PLAYER = "player"


urlpatterns = [
    path(
        f"{_BASE_PLAYER}/role/",
        RoleListView.as_view(),
        name="player-roles-list",
    ),
    path(
        f"{_BASE_PLAYER}/role/",
        RoleCreateView.as_view(),
        name="player-roles-create",
    ),
    path(
        f"{_BASE_PLAYER}/role/<int:role_id>/",
        RoleDetailView.as_view(),
        name="player-roles-detail",
    ),
    path(
        f"{_BASE_PLAYER}/role/<int:role_id>/",
        RoleUpdateView.as_view(),
        name="player-roles-update",
    ),
    path(
        f"{_BASE_PLAYER}/role/<int:role_id>/",
        RoleDeleteView.as_view(),
        name="player-roles-delete",
    ),
]

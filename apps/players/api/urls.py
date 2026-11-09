"""URL patterns for the players app."""

from django.urls import path

from apps.players.api.views import (
    AttributeDetailView,
    AttributeListCreateView,
    OverallFormulaActivateView,
    OverallFormulaActiveView,
    OverallFormulaDetailView,
    OverallFormulaListCreateView,
    OverallFormulaPreviewView,
    PlayerAttributeDetailView,
    PlayerAttributeListCreateView,
    PlayerDetailView,
    PlayerListCreateView,
    PlayerPhotoView,
    PlayerRoleDetailView,
    PlayerRoleListCreateView,
    RoleDetailView,
    RoleListCreateView,
)

_BASE_ROLE = "role"
_BASE_PLAYER = "player"
_BASE_ATTRIBUTE = "attribute"
_BASE_FORMULA = "overall-formula"

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
    path(
        f"{_BASE_ATTRIBUTE}/",
        AttributeListCreateView.as_view(),
        name="players-attribute-list-create",
    ),
    path(
        f"{_BASE_ATTRIBUTE}/<int:attribute_id>/",
        AttributeDetailView.as_view(),
        name="players-attribute-detail",
    ),
    path(
        f"{_BASE_PLAYER}/<int:player_id>/attribute/",
        PlayerAttributeListCreateView.as_view(),
        name="players-player-attribute-list-create",
    ),
    path(
        f"{_BASE_PLAYER}/<int:player_id>/attribute/<int:attribute_id>/",
        PlayerAttributeDetailView.as_view(),
        name="players-player-attribute-detail",
    ),
    path(
        f"{_BASE_PLAYER}/<int:player_id>/photo/",
        PlayerPhotoView.as_view(),
        name="players-player-photo",
    ),
    path(
        f"{_BASE_FORMULA}/",
        OverallFormulaListCreateView.as_view(),
        name="players-overall-formula-list-create",
    ),
    path(
        f"{_BASE_FORMULA}/active/",
        OverallFormulaActiveView.as_view(),
        name="players-overall-formula-active",
    ),
    path(
        f"{_BASE_FORMULA}/preview/",
        OverallFormulaPreviewView.as_view(),
        name="players-overall-formula-preview",
    ),
    path(
        f"{_BASE_FORMULA}/<int:formula_id>/",
        OverallFormulaDetailView.as_view(),
        name="players-overall-formula-detail",
    ),
    path(
        f"{_BASE_FORMULA}/<int:formula_id>/activate/",
        OverallFormulaActivateView.as_view(),
        name="players-overall-formula-activate",
    ),
]

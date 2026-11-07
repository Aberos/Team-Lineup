"""Root URL configuration for the TeamLineup project."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

_API = "api/v1/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"{_API}schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        f"{_API}docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(f"{_API}", include("apps.core.api.urls")),
    path(f"{_API}", include("apps.players.api.urls")),
    path(f"{_API}", include("apps.events.api.urls")),
]

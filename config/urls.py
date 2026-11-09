"""Root URL configuration for the TeamLineup project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
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

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

if settings.FRONTEND_INDEX.exists():
    urlpatterns += [
        re_path(
            r"^(?!api/|admin/|static/|media/).*$",
            TemplateView.as_view(template_name="index.html"),
            name="frontend",
        ),
    ]

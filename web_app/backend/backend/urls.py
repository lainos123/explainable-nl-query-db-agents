from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import api_root

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", api_root, name="api-root"),

    path("api/core/", include("core.urls")),

    path("api/agents/", include("agents.urls")),  # Temporarily commented out due to missing langchain dependencies

    path("api/utils/", include("utils.urls")),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

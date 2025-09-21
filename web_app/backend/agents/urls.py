from rest_framework.routers import DefaultRouter
from .views import AgentViewSet

router = DefaultRouter()
router.register(r"", AgentViewSet, basename="agents")

urlpatterns = router.urls
